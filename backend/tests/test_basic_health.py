from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_healthcheck():
    """Test that the health endpoint returns 200 and expected JSON."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["message"] == "200 OK!"