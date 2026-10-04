/**
 * Earth Analog Finder — Front-end Application
 * Interactive map, filtering, full-text search, details, and radar comparisons.
 */

document.addEventListener("DOMContentLoaded", () => {
    // --- State ---
    let map = null;
    let markersLayer = null;
    let userMarker = null;
    let locationsData = [];
    let compareIds = [];
    let currentDetailId = null;
    let radarChart = null;
    let searchDebounceTimer = null;

    // --- DOM Elements ---
    const searchInput = document.getElementById("search");
    const planetSelect = document.getElementById("planet");
    const typeSelect = document.getElementById("type");
    const minscoreInput = document.getElementById("minscore");
    const minscoreValue = document.getElementById("minscore-value");
    const sortSelect = document.getElementById("sort");
    const btnReset = document.getElementById("btn-reset");
    const statusEl = document.getElementById("status");
    const loaderEl = document.getElementById("loader");

    const detailPanel = document.getElementById("detail");
    const detailClose = document.getElementById("detail-close");
    const detailIcon = document.getElementById("detail-icon");
    const detailName = document.getElementById("detail-name");
    const detailMeta = document.getElementById("detail-meta");
    const detailDesc = document.getElementById("detail-desc");
    const detailBadges = document.getElementById("detail-badges");
    const detailScores = document.getElementById("detail-scores");
    const detailReasons = document.getElementById("detail-reasons");
    const detailSource = document.getElementById("detail-source");
    const detailAddCompare = document.getElementById("detail-add-compare");

    const btnNearest = document.getElementById("btn-nearest");
    const btnCompare = document.getElementById("btn-compare");
    const compareCount = document.getElementById("compare-count");
    const compareModal = document.getElementById("compare-modal");
    const compareClose = document.getElementById("compare-close");
    const compareChips = document.getElementById("compare-chips");
    const toastEl = document.getElementById("toast");

    // --- Type & Planet metadata helpers ---
    const TYPE_LABELS = {
        desert: "Cho'l",
        volcano: "Vulqon",
        cave: "G'or",
        glacier: "Muzlik",
        crater: "Krater",
        other: "Boshqa"
    };

    const TYPE_ICONS = {
        desert: "🏜️",
        volcano: "🌋",
        cave: "🕳️",
        glacier: "🧊",
        crater: "🌑",
        other: "🪐"
    };

    function getPlanetColor(bestPlanet) {
        if (bestPlanet === "moon") return "#b9c2d6";
        if (bestPlanet === "mars") return "#ff5a3c";
        return "#b06bff"; // both / balanced
    }

    function showToast(message, type = "ok", duration = 3500) {
        if (!toastEl) return;
        toastEl.textContent = message;
        toastEl.className = `toast ${type}`;
        toastEl.hidden = false;
        clearTimeout(toastEl._timer);
        toastEl._timer = setTimeout(() => {
            toastEl.hidden = true;
        }, duration);
    }

    function showLoader(show) {
        if (!loaderEl) return;
        loaderEl.hidden = !show;
        loaderEl.style.display = show ? "grid" : "none";
    }

    // --- Leaflet Map Init ---
    function initMap() {
        if (typeof L === "undefined") {
            console.error("Leaflet library not loaded yet.");
            setTimeout(initMap, 150);
            return;
        }

        map = L.map("map", {
            zoomControl: false,
            minZoom: 2,
            maxZoom: 18,
            worldCopyJump: true
        }).setView([20, 0], 2);

        L.control.zoom({ position: "bottomright" }).addTo(map);

        const osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap contributors'
        });

        const satellite = L.tileLayer(
            'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            { maxZoom: 18, attribution: 'Tiles &copy; Esri' }
        );

        const darkMatter = L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
            attribution: '&copy; OpenStreetMap &copy; CARTO',
            subdomains: "abcd",
            maxZoom: 19
        });

        // Add OSM as default layer
        osm.addTo(map);

        L.control.layers(
            {
                'Xarita': osm,
                'Sun\'iy yo\'ldosh': satellite,
                'Kosmik (Dark)': darkMatter
            },
            null,
            { position: 'topright' }
        ).addTo(map);

        markersLayer = L.layerGroup().addTo(map);

        // Close detail panel when map background is clicked
        map.on("click", (e) => {
            // Only if not clicked on a marker
            if (e.originalEvent && !e.originalEvent.target.closest(".leaflet-marker-icon, .leaflet-interactive")) {
                closeDetail();
            }
        });
    }

    // --- Markers Rendering ---
    function renderMarkers(items) {
        if (!markersLayer) return;
        markersLayer.clearLayers();

        items.forEach((loc) => {
            const color = getPlanetColor(loc.best_planet);
            const score = Math.round(loc.best_score || loc.mars_score || loc.moon_score || 0);
            const planetLabel = loc.best_planet === "mars" ? "Mars" : (loc.best_planet === "moon" ? "Oy" : "Oy / Mars");

            const marker = L.circleMarker([loc.lat, loc.lon], {
                radius: 8,
                fillColor: color,
                color: "#ffffff",
                weight: 1.5,
                opacity: 0.9,
                fillOpacity: 0.85,
                className: "marker-pulse"
            });

            marker.bindTooltip(`
                <div style="font-family: inherit; font-size: 12px; line-height: 1.4;">
                    <strong style="color: #fff; font-size: 13px;">${loc.name}</strong><br/>
                    <span style="color: #93a0c4;">${loc.country} · ${TYPE_LABELS[loc.type] || loc.type}</span><br/>
                    <span style="color: ${color}; font-weight: bold;">${planetLabel} analogi (${score}%)</span>
                </div>
            `, {
                direction: "top",
                offset: [0, -6],
                opacity: 0.96
            });

            marker.on("click", (e) => {
                L.DomEvent.stopPropagation(e);
                openDetail(loc.id);
            });

            marker.addTo(markersLayer);
        });
    }

    // --- Fetch Locations ---
    async function loadLocations() {
        showLoader(true);
        statusEl.className = "status";
        statusEl.textContent = "Yuklanmoqda…";

        const query = searchInput.value.trim();
        const planet = planetSelect.value;
        const type = typeSelect.value;
        const minscore = minscoreInput.value;
        const sort = sortSelect.value;

        try {
            let url;
            if (query.length >= 2) {
                // Use full-text search
                url = `/api/search?q=${encodeURIComponent(query)}&limit=50`;
            } else {
                const params = new URLSearchParams();
                if (planet) params.append("planet", planet);
                if (type) params.append("type", type);
                if (minscore > 0) params.append("min_score", minscore);
                if (sort) params.append("sort", sort);
                params.append("page_size", "100");
                url = `/api/locations?${params.toString()}`;
            }

            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();

            locationsData = data.items || [];
            renderMarkers(locationsData);

            statusEl.className = "status ok";
            statusEl.textContent = `${locationsData.length} ta analog topildi`;
        } catch (err) {
            console.error("Xatolik yuklashda:", err);
            statusEl.className = "status error";
            statusEl.textContent = "Yuklashda xatolik yuz berdi";
            showToast("Ma'lumotlarni yuklab bo'lmadi", "error");
        } finally {
            showLoader(false);
        }
    }

    // --- Detail Panel ---
    async function openDetail(locationId) {
        currentDetailId = locationId;
        showLoader(true);

        try {
            const res = await fetch(`/api/locations/${locationId}`);
            if (!res.ok) throw new Error("Joy topilmadi");
            const loc = await res.json();

            detailIcon.textContent = TYPE_ICONS[loc.type] || "🪐";
            detailName.textContent = loc.name;

            const elevText = loc.elevation_m !== null && loc.elevation_m !== undefined ? `${loc.elevation_m.toLocaleString()} m` : "Noma'lum balandlik";
            detailMeta.textContent = `${loc.country} · ${TYPE_LABELS[loc.type] || loc.type} · ${elevText}`;
            detailDesc.textContent = loc.description || "Tavsif mavjud emas.";

            // Badges
            detailBadges.innerHTML = "";
            const typeBadge = document.createElement("span");
            typeBadge.className = "badge badge-type";
            typeBadge.textContent = TYPE_LABELS[loc.type] || loc.type;
            detailBadges.appendChild(typeBadge);

            if (loc.is_estimated) {
                const estBadge = document.createElement("span");
                estBadge.className = "badge badge-estimated";
                estBadge.textContent = "Tahminiy (Estimated)";
                detailBadges.appendChild(estBadge);
            }

            // Scores
            const moonScore = Math.round(loc.moon_score || (loc.scores && loc.scores.find(s => s.planet === "moon")?.score) || 0);
            const marsScore = Math.round(loc.mars_score || (loc.scores && loc.scores.find(s => s.planet === "mars")?.score) || 0);

            detailScores.innerHTML = `
                <div class="score-row">
                    <div class="score-top">
                        <span>Oy analogi (Moon)</span>
                        <b style="color: #b9c2d6;">${moonScore}%</b>
                    </div>
                    <div class="bar bar-moon"><span style="width: ${moonScore}%"></span></div>
                </div>
                <div class="score-row">
                    <div class="score-top">
                        <span>Mars analogi (Mars)</span>
                        <b style="color: #ff5a3c;">${marsScore}%</b>
                    </div>
                    <div class="bar bar-mars"><span style="width: ${marsScore}%"></span></div>
                </div>
            `;

            // Reasons
            detailReasons.innerHTML = "";
            if (loc.curated_reasons && loc.curated_reasons.length > 0) {
                loc.curated_reasons.forEach(r => {
                    const li = document.createElement("li");
                    li.className = "curated";
                    const pName = r.planet === "mars" ? "Mars" : "Oy";
                    li.innerHTML = `<span class="reason-cat">${r.category} · ${pName} tahlili</span>${r.text}`;
                    detailReasons.appendChild(li);
                });
            }

            if (loc.reasons && loc.reasons.length > 0) {
                loc.reasons.slice(0, 4).forEach(r => {
                    const li = document.createElement("li");
                    li.innerHTML = `<span class="reason-cat">${r.category} · ${Math.round(r.contribution_pct)}% moslik</span>${r.text}`;
                    detailReasons.appendChild(li);
                });
            }

            // Source URL
            if (loc.source_url) {
                detailSource.href = loc.source_url;
                detailSource.hidden = false;
            } else {
                detailSource.hidden = true;
            }

            // Update Add/Remove compare button state
            updateDetailCompareButton();

            detailPanel.hidden = false;
            detailPanel.style.display = "block";

            // Pan map smoothly to the selected location
            if (map && loc.lat && loc.lon) {
                map.flyTo([loc.lat, loc.lon], Math.max(map.getZoom(), 5), { duration: 0.8 });
            }
        } catch (err) {
            console.error(err);
            showToast("Batafsil ma'lumotni yuklashda xatolik", "error");
        } finally {
            showLoader(false);
        }
    }

    function closeDetail() {
        if (!detailPanel) return;
        detailPanel.hidden = true;
        detailPanel.style.display = "none";
        currentDetailId = null;
    }

    function updateDetailCompareButton() {
        if (!currentDetailId) return;
        const isAdded = compareIds.includes(currentDetailId);
        if (isAdded) {
            detailAddCompare.textContent = "✓ Taqqoslashdan chiqarish";
            detailAddCompare.className = "btn btn-ghost";
        } else {
            detailAddCompare.textContent = "📊 Taqqoslashga qo'shish";
            detailAddCompare.className = "btn btn-accent";
        }
    }

    // --- Compare Management ---
    function updateCompareUI() {
        compareCount.textContent = compareIds.length;
        updateDetailCompareButton();
    }

    function toggleCompare(id) {
        const idx = compareIds.indexOf(id);
        if (idx >= 0) {
            compareIds.splice(idx, 1);
            showToast("Taqqoslash ro'yxatidan olib tashlandi");
        } else {
            if (compareIds.length >= 3) {
                showToast("Ko'pi bilan 3 ta joyni taqqoslash mumkin", "error");
                return;
            }
            compareIds.push(id);
            showToast("Taqqoslash ro'yxatiga qo'shildi", "ok");
        }
        updateCompareUI();
    }

    async function openCompareModal() {
        if (compareIds.length < 2) {
            showToast("Taqqoslash uchun kamida 2 ta analog tanlang", "error");
            return;
        }

        showLoader(true);
        try {
            const url = `/api/compare?ids=${compareIds.join(",")}`;
            const res = await fetch(url);
            if (!res.ok) throw new Error("Taqqoslash ma'lumotlarini olib bo'lmadi");
            const data = await res.json();

            // Render chips
            compareChips.innerHTML = "";
            data.datasets.forEach(ds => {
                const chip = document.createElement("span");
                chip.className = "chip";
                chip.innerHTML = `${ds.label} <button type="button" title="Olib tashlash">✕</button>`;
                chip.querySelector("button").addEventListener("click", () => {
                    toggleCompare(ds.location_id);
                    if (compareIds.length >= 2) {
                        openCompareModal();
                    } else {
                        closeCompareModal();
                    }
                });
                compareChips.appendChild(chip);
            });

            // Render Chart.js Radar Chart
            renderRadarChart(data);
            compareModal.hidden = false;
            compareModal.style.display = "grid";
        } catch (err) {
            console.error(err);
            showToast("Taqqoslashda xatolik yuz berdi", "error");
        } finally {
            showLoader(false);
        }
    }

    function closeCompareModal() {
        if (!compareModal) return;
        compareModal.hidden = true;
        compareModal.style.display = "none";
        if (radarChart) {
            radarChart.destroy();
            radarChart = null;
        }
    }

    function renderRadarChart(compareData) {
        const canvas = document.getElementById("radar-chart");
        if (!canvas || typeof Chart === "undefined") return;

        if (radarChart) {
            radarChart.destroy();
        }

        const colors = [
            { bg: "rgba(124, 92, 255, 0.25)", border: "#7c5cff", point: "#7c5cff" },
            { bg: "rgba(34, 211, 238, 0.25)", border: "#22d3ee", point: "#22d3ee" },
            { bg: "rgba(255, 90, 60, 0.25)", border: "#ff5a3c", point: "#ff5a3c" }
        ];

        const datasets = compareData.datasets.map((ds, idx) => {
            const c = colors[idx % colors.length];
            return {
                label: ds.label,
                data: ds.values,
                backgroundColor: c.bg,
                borderColor: c.border,
                pointBackgroundColor: c.point,
                pointBorderColor: "#fff",
                pointHoverBackgroundColor: "#fff",
                pointHoverBorderColor: c.point,
                borderWidth: 2,
                pointRadius: 4,
            };
        });

        radarChart = new Chart(canvas.getContext("2d"), {
            type: "radar",
            data: {
                labels: compareData.axis_labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        suggestedMin: 0,
                        suggestedMax: 100,
                        angleLines: { color: "rgba(255, 255, 255, 0.12)" },
                        grid: { color: "rgba(255, 255, 255, 0.08)" },
                        pointLabels: {
                            color: "#c3cde6",
                            font: { size: 12, weight: "bold" }
                        },
                        ticks: {
                            display: false,
                            stepSize: 20
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: "top",
                        labels: {
                            color: "#e9eeff",
                            font: { size: 13, weight: "600" },
                            padding: 16
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` ${ctx.dataset.label}: ${Math.round(ctx.raw)}%`
                        }
                    }
                }
            }
        });
    }

    // --- Nearest Analog Geolocation ---
    function findNearestAnalog() {
        if (!navigator.geolocation) {
            showToast("Brauzeringiz geolokatsiyani qo'llab-quvvatlamaydi", "error");
            return;
        }

        showToast("Joylashuvingiz aniqlanmoqda…", "ok", 5000);
        showLoader(true);

        navigator.geolocation.getCurrentPosition(
            async (pos) => {
                const lat = pos.coords.latitude;
                const lon = pos.coords.longitude;

                // Add or move user marker
                if (userMarker) {
                    userMarker.setLatLng([lat, lon]);
                } else {
                    userMarker = L.circleMarker([lat, lon], {
                        radius: 9,
                        fillColor: "#22d3ee",
                        color: "#ffffff",
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.95
                    }).addTo(map);
                    userMarker.bindTooltip("<b>Sizning joylashuvingiz</b>", { permanent: false, direction: "top" });
                }

                try {
                    const res = await fetch(`/api/nearest?lat=${lat}&lon=${lon}&limit=1`);
                    if (!res.ok) throw new Error("Eng yaqin analog topilmadi");
                    const data = await res.json();

                    if (data.items && data.items.length > 0) {
                        const nearest = data.items[0];
                        showToast(`Eng yaqin analog: ${nearest.name} (${nearest.distance_km} km)`, "ok", 4000);
                        openDetail(nearest.id);
                        map.flyTo([nearest.lat, nearest.lon], 6, { duration: 1.2 });
                    } else {
                        showToast("Yaqin atrofda analog topilmadi", "error");
                    }
                } catch (err) {
                    console.error(err);
                    showToast("Eng yaqin analogni aniqlashda xatolik", "error");
                } finally {
                    showLoader(false);
                }
            },
            (err) => {
                showLoader(false);
                console.warn("Geolokatsiya xatosi:", err);
                showToast("Geolokatsiyaga ruxsat berilmadi yoki xatolik yuz berdi", "error");
            },
            { timeout: 10000, enableHighAccuracy: true }
        );
    }

    // --- Event Listeners ---
    minscoreInput.addEventListener("input", () => {
        minscoreValue.textContent = `${minscoreInput.value}%`;
    });

    minscoreInput.addEventListener("change", () => {
        loadLocations();
    });

    planetSelect.addEventListener("change", loadLocations);
    typeSelect.addEventListener("change", loadLocations);
    sortSelect.addEventListener("change", loadLocations);

    searchInput.addEventListener("input", () => {
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(() => {
            loadLocations();
        }, 300);
    });

    btnReset.addEventListener("click", () => {
        searchInput.value = "";
        planetSelect.value = "";
        typeSelect.value = "";
        minscoreInput.value = "0";
        minscoreValue.textContent = "0%";
        sortSelect.value = "score";
        loadLocations();
    });

    detailClose.addEventListener("click", closeDetail);

    detailAddCompare.addEventListener("click", () => {
        if (currentDetailId) {
            toggleCompare(currentDetailId);
        }
    });

    btnCompare.addEventListener("click", openCompareModal);
    compareClose.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        closeCompareModal();
    });

    compareModal.addEventListener("click", (e) => {
        if (e.target === compareModal) {
            closeCompareModal();
        }
    });

    btnNearest.addEventListener("click", findNearestAnalog);

    // ESC key closes panels/modals
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            if (!compareModal.hidden || compareModal.style.display !== "none") closeCompareModal();
            else if (!detailPanel.hidden || detailPanel.style.display !== "none") closeDetail();
        }
    });

    // --- Start ---
    closeDetail();
    closeCompareModal();
    showLoader(false);
    initMap();
    loadLocations();
});
