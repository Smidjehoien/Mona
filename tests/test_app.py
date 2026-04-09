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
    """Test the hello world endpoint"""
    response = client.get("/hello")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Ahoi" in data["message"]
    assert "Mergington High School" in data["message"]


def test_signup_email_edge_cases():
    """Test various invalid email formats"""
    invalid_emails = [
        "notanemail",
        "@mergington.edu",
        "test@",
        "test@@mergington.edu",
        "test @mergington.edu",
        "test@mergington",
        "",
        "test@.edu"
    ]

    for email in invalid_emails:
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response.status_code == 400, f"Expected 400 for email: {email}"
        assert "Invalid email format" in response.json()["detail"]


def test_signup_valid_email_variations():
    """Test that various valid email formats are accepted"""
    valid_emails = [
        "test.user@mergington.edu",
        "test_user@mergington.edu",
        "test123@mergington.edu",
        "TEST@MERGINGTON.EDU",
        "test..double@mergington.edu"  # Consecutive dots are allowed by the regex
    ]

    for email in valid_emails:
        response = client.post(f"/activities/Basketball Team/signup?email={email}")
        assert response.status_code == 200, f"Expected 200 for valid email: {email}"
        # Clean up
        client.delete(f"/activities/Basketball Team/signup?email={email}")


def test_skills_accumulation_multiple_activities():
    """Test that skills accumulate from multiple activities"""
    email = "multiskills@mergington.edu"

    # Sign up for multiple activities with different skills
    client.post(f"/activities/Chess Club/signup?email={email}")
    client.post(f"/activities/Programming Class/signup?email={email}")

    # Get skills
    response = client.get(f"/skills/{email}")
    assert response.status_code == 200
    data = response.json()
    skills = data["skills"]

    # Should have skills from both activities
    # Chess Club: Strategic Thinking, Problem Solving, Critical Analysis
    # Programming Class: Coding, Problem Solving, Logical Thinking, Debugging
    assert len(skills) >= 6  # At least 6 unique skills (Problem Solving is shared)
    assert "Strategic Thinking" in skills
    assert "Coding" in skills
    assert "Problem Solving" in skills

    # Clean up
    client.delete(f"/activities/Chess Club/signup?email={email}")
    client.delete(f"/activities/Programming Class/signup?email={email}")


def test_activity_name_with_spaces():
    """Test activity names with spaces are handled correctly"""
    # This tests URL encoding of activity names
    email = "spacename@mergington.edu"

    # "Chess Club" has a space in it
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 200

    # Verify the signup worked
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities["Chess Club"]["participants"]

    # Clean up
    client.delete(f"/activities/Chess Club/signup?email={email}")


def test_get_skills_with_various_email_formats():
    """Test get_skills endpoint with different valid email formats"""
    email = "format.test123@mergington.edu"  # Avoid + which requires URL encoding

    # Sign up to create skills
    signup_response = client.post(f"/activities/Science Club/signup?email={email}")
    assert signup_response.status_code == 200

    # Get skills with the same email format
    response = client.get(f"/skills/{email}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert len(data["skills"]) > 0

    # Clean up
    client.delete(f"/activities/Science Club/signup?email={email}")


def test_activities_structure_complete():
    """Test that all activities have complete required fields"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()

    required_fields = ["description", "schedule", "max_participants", "participants", "skills"]

    for activity_name, activity_data in activities.items():
        for field in required_fields:
            assert field in activity_data, f"Activity '{activity_name}' missing field '{field}'"

        # Validate field types
        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)
        assert isinstance(activity_data["skills"], list)

        # Validate reasonable values
        assert activity_data["max_participants"] > 0
        assert len(activity_data["description"]) > 0
        assert len(activity_data["schedule"]) > 0


def test_concurrent_signups_dont_exceed_capacity():
    """Test that concurrent-like signups respect capacity limits"""
    activity_name = "Swimming Club"

    # Get activity details
    activities = client.get("/activities").json()
    activity = activities[activity_name]
    max_cap = activity["max_participants"]
    current = len(activity["participants"])

    # Fill to capacity
    emails = []
    for i in range(current, max_cap):
        email = f"concurrent{i}@mergington.edu"
        emails.append(email)
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200

    # Verify activity is at capacity
    activities = client.get("/activities").json()
    assert len(activities[activity_name]["participants"]) == max_cap

    # Try to add one more
    overflow = "overflow@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={overflow}")
    assert response.status_code == 400
    assert "maximum capacity" in response.json()["detail"]

    # Clean up
    for email in emails:
        client.delete(f"/activities/{activity_name}/signup?email={email}")


def test_skills_unique_no_duplicates():
    """Test that signing up for activity with overlapping skills doesn't duplicate"""
    email = "uniqueskills@mergington.edu"

    # Sign up for two activities that share "Problem Solving" skill
    # Chess Club has: Strategic Thinking, Problem Solving, Critical Analysis
    # Programming Class has: Coding, Problem Solving, Logical Thinking, Debugging
    client.post(f"/activities/Chess Club/signup?email={email}")
    client.post(f"/activities/Programming Class/signup?email={email}")

    # Get skills
    response = client.get(f"/skills/{email}")
    skills = response.json()["skills"]

    # Convert to set and back to list to check for duplicates
    unique_skills = list(set(skills))
    assert len(skills) == len(unique_skills), "Skills list contains duplicates"

    # Problem Solving should appear exactly once
    assert skills.count("Problem Solving") <= 1

    # Clean up
    client.delete(f"/activities/Chess Club/signup?email={email}")
    client.delete(f"/activities/Programming Class/signup?email={email}")