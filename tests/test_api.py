
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_home_endpoint():
    """The backend home endpoint should respond successfully."""
    response = client.get("/")
    assert response.status_code == 200


def test_health_endpoint():
    """The health endpoint should confirm the model is loaded."""
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True


def test_prediction_requires_an_image():
    """The prediction endpoint should reject a request without an image."""
    response = client.post("/predict")

    assert response.status_code == 422


def test_prediction_rejects_invalid_image():
    """The prediction endpoint should reject invalid image data."""
    response = client.post(
        "/predict",
        files={
            "file": (
                "invalid.jpg",
                b"this is not a real image",
                "image/jpeg",
            )
        },
    )

    assert response.status_code >= 400
