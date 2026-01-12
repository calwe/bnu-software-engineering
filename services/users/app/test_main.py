from fastapi.testclient import TestClient
import os
from .main import app

client = TestClient(app)

def test_login():
    response = client.post(
        "/login",
        json={"username": "test", "password": "test"}
    )
    assert response.status_code == 200

def test_get_session():
    response = client.get(
        "/getSession",
        headers={"Authorization": f"Bearer {os.getenv('TEST_TOKEN')}"}
    )
    assert response.status_code == 200

def test_get_session_invalid_token():
    response = client.get(
        "/getSession",
        headers={"Authorization": f"Bearer 123"}
    )
    assert response.status_code == 401

