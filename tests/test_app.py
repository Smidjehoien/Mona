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


def test_signup_invalid_email():
    """Test signing up with invalid email format"""
    response = client.post("/activities/Chess Club/signup?email=invalid-email")
    assert response.status_code == 400
    assert "Invalid email format" in response.json()["detail"]


def test_unregister_invalid_email():
    """Test unregistering with invalid email format"""
    response = client.delete("/activities/Chess Club/signup?email=invalid-email")
    assert response.status_code == 400
    assert "Invalid email format" in response.json()["detail"]


def test_hello_endpoint():
    """Test the hello endpoint returns welcome message"""
    response = client.get("/hello")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Mergington High School" in data["message"]


def test_email_validation_edge_cases():
    """Test various invalid email formats"""
    invalid_emails = [
        "invalid",  # No @ or domain
        "@mergington.edu",  # Missing local part
        "test@",  # Missing domain
        "test@@mergington.edu",  # Double @
        "test@mergington",  # Missing TLD
        "test .space@mergington.edu",  # Space in local part
        "test@merger ington.edu",  # Space in domain
        "",  # Empty string
        "test@.edu",  # Domain starts with dot
    ]

    for email in invalid_emails:
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response.status_code == 400, f"Email '{email}' should be invalid"
        assert "Invalid email format" in response.json()["detail"]


def test_valid_email_edge_cases():
    """Test various valid email formats"""
    import urllib.parse

    valid_emails = [
        "test.name@mergington.edu",
        "test+tag@mergington.edu",
        "test_underscore@mergington.edu",
        "123@mergington.edu",
        "test@sub.mergington.edu",
    ]

    for email in valid_emails:
        # URL-encode the email to handle special characters like +
        encoded_email = urllib.parse.quote(email, safe='@')

        # Sign up
        response = client.post(f"/activities/Basketball Team/signup?email={encoded_email}")
        assert response.status_code == 200, f"Email '{email}' should be valid"

        # Clean up
        client.delete(f"/activities/Basketball Team/signup?email={encoded_email}")


def test_skills_accumulation_multiple_activities():
    """Test that skills accumulate when signing up for multiple activities"""
    email = "multiskill@mergington.edu"

    # Sign up for Programming Class (has Coding, Problem Solving, Logical Thinking, Debugging)
    client.post(f"/activities/Programming Class/signup?email={email}")
    skills_after_first = set(client.get(f"/skills/{email}").json()["skills"])
    assert len(skills_after_first) >= 4

    # Sign up for Chess Club (has Strategic Thinking, Problem Solving, Critical Analysis)
    client.post(f"/activities/Chess Club/signup?email={email}")
    skills_after_second = set(client.get(f"/skills/{email}").json()["skills"])

    # Should have more skills now (union of both activities)
    assert len(skills_after_second) > len(skills_after_first)
    # Should include skills from both activities
    assert skills_after_first.issubset(skills_after_second)

    # Clean up
    client.delete(f"/activities/Programming Class/signup?email={email}")
    client.delete(f"/activities/Chess Club/signup?email={email}")


def test_activity_name_with_spaces():
    """Test that activity names with spaces work correctly (URL encoding)"""
    # Activity names with spaces should work (they're in URL path)
    response = client.post("/activities/Chess Club/signup?email=spaces@mergington.edu")
    assert response.status_code == 200

    # Clean up
    client.delete("/activities/Chess Club/signup?email=spaces@mergington.edu")


def test_signup_then_check_in_participants_list():
    """Test that signed up student appears in activity's participants list"""
    email = "checkparticipants@mergington.edu"
    activity_name = "Swimming Club"

    # Get initial participants
    activities_before = client.get("/activities").json()
    participants_before = activities_before[activity_name]["participants"]

    # Sign up
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Check that student is now in participants list
    activities_after = client.get("/activities").json()
    participants_after = activities_after[activity_name]["participants"]

    assert email in participants_after
    assert email not in participants_before
    assert len(participants_after) == len(participants_before) + 1

    # Clean up
    client.delete(f"/activities/{activity_name}/signup?email={email}")


def test_all_activities_have_required_fields():
    """Test that all activities have the required structure"""
    response = client.get("/activities")
    activities = response.json()

    required_fields = ["description", "schedule", "max_participants", "participants", "skills"]

    for activity_name, activity_data in activities.items():
        for field in required_fields:
            assert field in activity_data, f"Activity '{activity_name}' missing field '{field}'"

        # Validate types
        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)
        assert isinstance(activity_data["skills"], list)

        # Validate constraints
        assert activity_data["max_participants"] > 0
        assert len(activity_data["participants"]) <= activity_data["max_participants"]


def test_skills_endpoint_returns_list_not_set():
    """Test that skills endpoint returns a list, not a set"""
    email = "listcheck@mergington.edu"

    # Sign up to get some skills
    client.post(f"/activities/Drama Club/signup?email={email}")

    # Get skills
    response = client.get(f"/skills/{email}")
    data = response.json()

    # Should be a list (JSON serializable)
    assert isinstance(data["skills"], list)

    # Clean up
    client.delete(f"/activities/Drama Club/signup?email={email}")


def test_case_sensitive_activity_names():
    """Test that activity names are case-sensitive"""
    # Correct case should work
    response_correct = client.post("/activities/Chess Club/signup?email=case1@mergington.edu")
    assert response_correct.status_code == 200

    # Incorrect case should fail
    response_wrong = client.post("/activities/chess club/signup?email=case2@mergington.edu")
    assert response_wrong.status_code == 404
    assert "Activity not found" in response_wrong.json()["detail"]

    # Clean up
    client.delete("/activities/Chess Club/signup?email=case1@mergington.edu")


def test_multiple_students_same_activity():
    """Test that multiple students can sign up for the same activity"""
    activity_name = "Art Studio"
    emails = ["artist1@mergington.edu", "artist2@mergington.edu", "artist3@mergington.edu"]

    # Sign up multiple students
    for email in emails:
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200

    # Verify all are in participants list
    activities = client.get("/activities").json()
    participants = activities[activity_name]["participants"]

    for email in emails:
        assert email in participants

    # Clean up
    for email in emails:
        client.delete(f"/activities/{activity_name}/signup?email={email}")


def test_unregister_removes_from_participants():
    """Test that unregistering removes student from participants list"""
    email = "removetest@mergington.edu"
    activity_name = "Debate Team"

    # Sign up
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Verify in list
    activities_after_signup = client.get("/activities").json()
    assert email in activities_after_signup[activity_name]["participants"]

    # Unregister
    client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Verify not in list
    activities_after_unregister = client.get("/activities").json()
    assert email not in activities_after_unregister[activity_name]["participants"]


def test_signup_with_very_long_email():
    """Test signup with a very long but valid email address"""
    # Create a valid but very long email
    long_local = "a" * 50
    long_email = f"{long_local}@mergington.edu"

    response = client.post(f"/activities/Science Club/signup?email={long_email}")
    assert response.status_code == 200

    # Clean up
    client.delete(f"/activities/Science Club/signup?email={long_email}")