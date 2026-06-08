"""Pytest configuration and fixtures for the API tests"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, get_default_activities, get_activities_db


@pytest.fixture
def test_activities():
    """Provide a fresh copy of activities data for each test"""
    return get_default_activities()


@pytest.fixture
def client(test_activities):
    """Provide a TestClient with overridden activities dependency"""
    
    def get_test_activities():
        return test_activities
    
    # Override the dependency to use test data
    app.dependency_overrides[get_activities_db] = get_test_activities
    
    yield TestClient(app)
    
    # Clean up after test
    app.dependency_overrides.clear()
