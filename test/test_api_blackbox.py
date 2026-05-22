# pyrefly: ignore [missing-import]
import pytest
import requests
import json

API_URL = "http://localhost:8000/chat"

def test_api_healthy():
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200

def test_chat_endpoint_valid_request():
    payload = {"message": "Apa itu sakramen baptis?", "mode": "short"}
    # The server returns a StreamingResponse (SSE)
    response = requests.post(API_URL, json=payload, stream=True)
    
    assert response.status_code == 200
    
    # Collect the streamed response
    full_response = ""
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            if decoded_line.startswith("data: "):
                full_response += decoded_line[6:]
    
    assert len(full_response) > 0
    # The current implementation just streams the text, not necessarily JSON-wrapped objects in each chunk
    # But it should contain some answer.

def test_chat_endpoint_missing_message():
    payload = {} # Missing 'message'
    response = requests.post(API_URL, json=payload)
    assert response.status_code == 422 # Unprocessable Entity (FastAPI standard)
