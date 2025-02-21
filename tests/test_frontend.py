import pytest
import json
import os

@pytest.fixture
def client(load_app):
    with load_app.test_client() as client:
        yield client

# Test for reaching the homepage successfully
def test_get_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    # Check that a form is displayed
    assert b"<form" in response.data