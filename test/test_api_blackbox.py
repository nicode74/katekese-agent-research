# pyrefly: ignore [missing-import]
import pytest
import requests

API_URL = "http://localhost:8000/api/chat"

@pytest.mark.skip(reason="API server might not be running during test execution")
def test_api_healthy():
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200

@pytest.mark.skip(reason="API server might not be running during test execution")
def test_chat_endpoint_valid_request():
    payload = {"query": "Apa itu sakramen baptis?"}
    response = requests.post(API_URL, json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert len(data["sources"]) > 0

@pytest.mark.skip(reason="API server might not be running during test execution")
def test_chat_endpoint_missing_query():
    payload = {}
    response = requests.post(API_URL, json=payload)
    assert response.status_code == 422 # Unprocessable Entity (FastAPI standard)
