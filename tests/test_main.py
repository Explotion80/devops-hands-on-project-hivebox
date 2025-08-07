from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()

def test_temperature():
    response = client.get("/temperature")
    assert response.status_code == 200