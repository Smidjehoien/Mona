"""
Tests for the Mergington High School Activities API
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirects_to_static():
    """Test that root path redirects to static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    """Test fetching all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    # Check that we have activities
    assert isinstance(data, dict)
    assert len(data) > 0
    
    # Check structure of first activity
    first_activity = list(data.values())[0]
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert "skills" in first_activity


def test_signup_success():
    """Test successfully signing up for an activity"""
    response = client.post(
        "/activities/Chess Club/signup?email=test@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@mergington.edu" in data["message"]
    
    # Clean up: unregister the test user
    client.delete("/activities/Chess Club/signup?email=test@mergington.edu")


def test_signup_duplicate():
    """Test that duplicate signups are prevented"""
    email = "duplicate@mergington.edu"
    
    # First signup should succeed
    response1 = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response1.status_code == 200
    
    # Second signup should fail
    response2 = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]
    
    # Clean up
    client.delete(f"/activities/Chess Club/signup?email={email}")


def test_signup_activity_not_found():
    """Test signing up for non-existent activity"""
    response = client.post(
        "/activities/NonExistent Activity/signup?email=test@mergington.edu"
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_capacity_check():
    """Test that signup respects maximum capacity"""
    # Get an activity with max_participants
    activities_response = client.get("/activities")
    activities = activities_response.json()
    
    # Find an activity and fill it to capacity
    test_activity = "Programming Class"
    activity = activities[test_activity]
    max_participants = activity["max_participants"]
    current_count = len(activity["participants"])
    
    # Try to add students until we hit capacity
    test_emails = []
    for i in range(current_count, max_participants):
        email = f"student{i}@mergington.edu"
        test_emails.append(email)
        response = client.post(f"/activities/{test_activity}/signup?email={email}")
        assert response.status_code == 200
    
    # Now try to add one more - should fail
    overflow_email = f"overflow@mergington.edu"
    response = client.post(f"/activities/{test_activity}/signup?email={overflow_email}")
    assert response.status_code == 400
    assert "maximum capacity" in response.json()["detail"]
    
    # Clean up
    for email in test_emails:
        client.delete(f"/activities/{test_activity}/signup?email={email}")


def test_unregister_success():
    """Test successfully unregistering from an activity"""
    email = "unregister@mergington.edu"
    
    # First sign up
    signup_response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert signup_response.status_code == 200
    
    # Then unregister
    unregister_response = client.delete(f"/activities/Chess Club/signup?email={email}")
    assert unregister_response.status_code == 200
    data = unregister_response.json()
    assert "message" in data
    assert email in data["message"]


def test_unregister_not_signed_up():
    """Test unregistering when not signed up"""
    response = client.delete(
        "/activities/Chess Club/signup?email=notsignedup@mergington.edu"
    )
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]


def test_unregister_activity_not_found():
    """Test unregistering from non-existent activity"""
    response = client.delete(
        "/activities/NonExistent Activity/signup?email=test@mergington.edu"
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_get_skills_success():
    """Test getting skills for a student"""
    # Sign up for an activity to gain skills
    email = "skills@mergington.edu"
    client.post(f"/activities/Programming Class/signup?email={email}")
    
    # Get skills
    response = client.get(f"/skills/{email}")
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "skills" in data
    assert email == data["email"]
    assert isinstance(data["skills"], list)
    assert len(data["skills"]) > 0
    
    # Clean up
    client.delete(f"/activities/Programming Class/signup?email={email}")


def test_get_skills_invalid_email():
    """Test getting skills with invalid email format"""
    response = client.get("/skills/invalid-email")
    assert response.status_code == 400
    assert "Invalid email format" in response.json()["detail"]


def test_get_skills_no_skills():
    """Test getting skills for student with no activities"""
    response = client.get("/skills/newstudent@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert data["skills"] == []


def test_skills_persist_after_unregister():
    """Test that skills are retained after unregistering from activity"""
    email = "persistent@mergington.edu"
    
    # Sign up for an activity
    client.post(f"/activities/Programming Class/signup?email={email}")
    
    # Get skills
    skills_before = client.get(f"/skills/{email}").json()["skills"]
    assert len(skills_before) > 0
    
    # Unregister
    client.delete(f"/activities/Programming Class/signup?email={email}")
    
    # Check skills are still there
    skills_after = client.get(f"/skills/{email}").json()["skills"]
    assert skills_after == skills_before
