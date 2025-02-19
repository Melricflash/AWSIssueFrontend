import json

import pytest
from app import app
from unittest.mock import patch

@pytest.fixture
def client():
    # Configure Flask app for testing
    app.config['TESTING'] = True
    app.config['DEBUG'] = False

    # Create a test client
    with app.test_client() as client:
        yield client

# Check if the form exists when loading the homepage
def test_get_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<form" in response.data

@patch("app.sqs.send_message") # Decorator to avoid sending to SQS
# Test valid data being sent
def test_post_valid_data(mock_send_message, client):
    # Simulate expected response
    mock_send_message.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

    data = {
        "title": "Test Title",
        "description": "Test Description",
        "priority": 1
    }

    # Post the data to the view
    response = client.post("/", data=data, content_type="application/x-www-form-urlencoded")

    assert response.status_code == 302
    mock_send_message.assert_called_once()

@patch("app.sqs.send_message")
def test_post_valid_json_data(client):

    data = {
        "title": "Test Title",
        "description": "Test Description",
        "priority": 1
    }

    response = client.post("/", data=json.dumps(data), content_type="application/json")
    assert response.status_code != 500


# Test invalid data being sent to the view
def test_post_invalid_priority(client):

    data = {
        "title": "Test Title",
        "description": "Test Description",
        "priority": 5
    }

    # JSON response directly to the view
    response = client.post("/", data=json.dumps(data), content_type="application/json")

    assert response.status_code == 500

# Test missing JSON fields when sending to view
def test_post_missing_fields(client):
    data = {
        "title": "Test Title"
    }

    # JSON response directly to the view
    response = client.post("/", data=json.dumps(data), content_type="application/json")
    assert response.status_code == 500

