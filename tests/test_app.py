import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original_activities = {}
    for name, details in activities.items():
        original_activities[name] = {
            "description": details["description"],
            "schedule": details["schedule"],
            "max_participants": details["max_participants"],
            "participants": details["participants"].copy()
        }

    yield

    # Reset to original state
    activities.clear()
    activities.update(original_activities)


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_successful(client, reset_activities):
    """Test successful signup"""
    # Sign up for an activity with no participants
    response = client.post("/activities/Basketball%20Team/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up newstudent@mergington.edu for Basketball Team" in data["message"]

    # Check that the participant was added
    response = client.get("/activities")
    data = response.json()
    assert "newstudent@mergington.edu" in data["Basketball Team"]["participants"]


def test_signup_already_signed_up(client):
    """Test signing up when already signed up"""
    # First signup
    response = client.post("/activities/Chess%20Club/signup?email=michael@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up for this activity" in data["detail"]


def test_signup_activity_not_found(client):
    """Test signing up for non-existent activity"""
    response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_successful(client, reset_activities):
    """Test successful unregister"""
    # First sign up
    client.post("/activities/Basketball%20Team/signup?email=temp@mergington.edu")

    # Then unregister
    response = client.delete("/activities/Basketball%20Team/unregister?email=temp@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered temp@mergington.edu from Basketball Team" in data["message"]

    # Check that the participant was removed
    response = client.get("/activities")
    data = response.json()
    assert "temp@mergington.edu" not in data["Basketball Team"]["participants"]


def test_unregister_not_signed_up(client):
    """Test unregistering when not signed up"""
    response = client.delete("/activities/Chess%20Club/unregister?email=notsignedup@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "Student not signed up for this activity" in data["detail"]


def test_unregister_activity_not_found(client):
    """Test unregistering from non-existent activity"""
    response = client.delete("/activities/NonExistent/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]