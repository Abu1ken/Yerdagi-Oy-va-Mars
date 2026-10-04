import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["locations"] >= 30

def test_api_root(client):
    res = client.get("/api")
    assert res.status_code == 200
    data = res.json()
    assert "docs" in data

def test_list_locations(client):
    res = client.get("/api/locations")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 30
    assert len(data["items"]) > 0

def test_filter_planet(client):
    res = client.get("/api/locations?planet=mars")
    assert res.status_code == 200
    data = res.json()
    assert all(item["mars_score"] is not None for item in data["items"])

def test_location_detail(client):
    res = client.get("/api/locations/1")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert "features" in data
    assert "scores" in data
    assert "reasons" in data

def test_search(client):
    res = client.get("/api/search?q=mars")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] > 0

def test_top(client):
    res = client.get("/api/top?planet=moon&k=3")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] == 3

def test_compare(client):
    res = client.get("/api/compare?ids=1,2")
    assert res.status_code == 200
    data = res.json()
    assert len(data["datasets"]) == 2
    assert len(data["axes"]) > 0

def test_nearest(client):
    res = client.get("/api/nearest?lat=41.311&lon=69.240")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] > 0
    assert "distance_km" in data["items"][0]

def test_static_html(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "Earth Analog Finder" in res.text
    assert "/app.js" in res.text
