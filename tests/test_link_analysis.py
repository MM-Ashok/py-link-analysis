from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_rejects_invalid_scheme():
    response = client.post("/link-analysis", json={"url": "file:///etc/passwd"})
    assert response.status_code == 422

def test_rejects_localhost():
    response = client.post("/link-analysis", json={"url": "http://localhost:8000"})
    assert response.status_code == 422
