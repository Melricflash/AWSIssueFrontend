import json
import os
import pytest
from moto import mock_aws
import boto3

@pytest.fixture
def client(load_app):
    with load_app.test_client() as client:
        yield client

# Test to see if our queues are set up correctly
def test_queue_setup():
    client = boto3.client("sqs", region_name="eu-north-1")
    result = client.list_queues()

    assert "QueueUrls" in result
    assert len(result["QueueUrls"]) == 3

# Test to check a successful payload
def test_send_to_queue_json(client, setup_sqs_queues, mocker):

    # Patch out LLM functionality
    mocker.patch("app.ask_llm", return_value = "Test LLM")

    # Create a mock json request
    payload = {
        "title": "Test Title",
        "description": "Test Description",
        "priority": 1
    }

    # Send POST to the view
    response = client.post("/", json=payload)

    # Check for redirect after successful response
    assert response.status_code == 302

# Test to check invalid priority in json
def test_send_invalid_json(client, setup_sqs_queues):

    # Create a mock json request
    payload = {
        "title": "Test Title",
        "description": "Test Description",
        "priority": 9
    }

    # Send POST to the view
    response = client.post("/", json=payload)

    assert response.status_code == 500


# Test to check missing json fields
def test_send_missing_json(client, setup_sqs_queues):

    # Create a mock json request
    payload = {
        "title": "Test Title"
    }

    # Send POST to the view
    response = client.post("/", json=payload)

    assert response.status_code == 500

# Test to check invalid priority in json
def test_send_empty_json(client, setup_sqs_queues):

    # Create a mock json request
    payload = {
        "title": "",
        "description": "",
        "priority": 1
    }

    # Send POST to the view
    response = client.post("/", json=payload)

    assert response.status_code == 500

