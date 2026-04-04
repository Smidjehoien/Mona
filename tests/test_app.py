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


def test_signup_email_validation_edge_cases():
    """Test that various invalid email formats are rejected by signup"""
    invalid_emails = [
        "invalid",
        "@mergington.edu",
        "test@",
        "test@@mergington.edu",
        "test@mergington",
        "test @mergington.edu",
        "test@merger ington.edu",
        "test@.edu",
    ]
    for email in invalid_emails:
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response.status_code == 400, f"Email '{email}' should be invalid"
        assert "Invalid email format" in response.json()["detail"]


def test_signup_valid_email_edge_cases():
    """Test that valid but unusual email formats are accepted by signup"""
    import urllib.parse

    valid_emails = [
        "test.name@mergington.edu",
        "test+tag@mergington.edu",
        "test_underscore@mergington.edu",
        "123@mergington.edu",
        "test@sub.mergington.edu",
    ]
    for email in valid_emails:
        encoded_email = urllib.parse.quote(email, safe="@")
        response = client.post(f"/activities/Basketball Team/signup?email={encoded_email}")
        assert response.status_code == 200, f"Email '{email}' should be valid"
        client.delete(f"/activities/Basketball Team/signup?email={encoded_email}")


def test_signup_adds_student_to_participants():
    """Test that after signup the student appears in the activity's participants list"""
    email = "checkparticipants@mergington.edu"
    activity_name = "Swimming Club"

    activities_before = client.get("/activities").json()
    participants_before = activities_before[activity_name]["participants"]

    client.post(f"/activities/{activity_name}/signup?email={email}")

    activities_after = client.get("/activities").json()
    participants_after = activities_after[activity_name]["participants"]

    assert email in participants_after
    assert email not in participants_before
    assert len(participants_after) == len(participants_before) + 1

    client.delete(f"/activities/{activity_name}/signup?email={email}")


def test_signup_response_message_contains_email_and_activity():
    """Test that signup response message contains the email and activity name"""
    email = "msgcheck@mergington.edu"
    activity_name = "Art Studio"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert email in data["message"]
    assert activity_name in data["message"]

    client.delete(f"/activities/{activity_name}/signup?email={email}")


def test_signup_activity_name_case_sensitive():
    """Test that activity name matching is case-sensitive"""
    response_correct = client.post("/activities/Chess Club/signup?email=case1@mergington.edu")
    assert response_correct.status_code == 200

    response_wrong_case = client.post("/activities/chess club/signup?email=case2@mergington.edu")
    assert response_wrong_case.status_code == 404
    assert "Activity not found" in response_wrong_case.json()["detail"]

    client.delete("/activities/Chess Club/signup?email=case1@mergington.edu")


def test_signup_activity_name_with_spaces():
    """Test that activity names containing spaces work correctly"""
    response = client.post("/activities/Chess Club/signup?email=spaces@mergington.edu")
    assert response.status_code == 200
    client.delete("/activities/Chess Club/signup?email=spaces@mergington.edu")


def test_signup_multiple_students_same_activity():
    """Test that multiple distinct students can sign up for the same activity"""
    activity_name = "Art Studio"
    emails = ["artist1@mergington.edu", "artist2@mergington.edu", "artist3@mergington.edu"]

    for email in emails:
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200

    participants = client.get("/activities").json()[activity_name]["participants"]
    for email in emails:
        assert email in participants

    for email in emails:
        client.delete(f"/activities/{activity_name}/signup?email={email}")


def test_signup_with_very_long_valid_email():
    """Test that a very long but valid email address is accepted"""
    long_local = "a" * 50
    long_email = f"{long_local}@mergington.edu"

    response = client.post(f"/activities/Science Club/signup?email={long_email}")
    assert response.status_code == 200

    client.delete(f"/activities/Science Club/signup?email={long_email}")


def test_signup_grants_activity_skills():
    """Test that the exact skills from the activity are added to the student on signup"""
    email = "skillgrant@mergington.edu"

    response = client.post(f"/activities/Drama Club/signup?email={email}")
    assert response.status_code == 200

    skills_response = client.get(f"/skills/{email}")
    assert skills_response.status_code == 200
    skills = set(skills_response.json()["skills"])

    expected_skills = {"Public Speaking", "Confidence", "Creativity", "Teamwork"}
    assert expected_skills.issubset(skills)

    client.delete(f"/activities/Drama Club/signup?email={email}")


def test_signup_skills_accumulate_across_activities():
    """Test that skills from multiple activities accumulate (union) on the student"""
    email = "multiskill@mergington.edu"

    client.post(f"/activities/Programming Class/signup?email={email}")
    skills_after_first = set(client.get(f"/skills/{email}").json()["skills"])
    assert len(skills_after_first) >= 4

    client.post(f"/activities/Chess Club/signup?email={email}")
    skills_after_second = set(client.get(f"/skills/{email}").json()["skills"])

    assert len(skills_after_second) > len(skills_after_first)
    assert skills_after_first.issubset(skills_after_second)

    client.delete(f"/activities/Programming Class/signup?email={email}")
    client.delete(f"/activities/Chess Club/signup?email={email}")


def test_signup_skills_not_duplicated_for_overlapping_activities():
    """Test that overlapping skills between activities are deduplicated"""
    email = "dedupecheck@mergington.edu"

    # Chess Club and Programming Class both have "Problem Solving"
    client.post(f"/activities/Chess Club/signup?email={email}")
    client.post(f"/activities/Programming Class/signup?email={email}")

    skills = client.get(f"/skills/{email}").json()["skills"]
    assert skills.count("Problem Solving") == 1

    client.delete(f"/activities/Chess Club/signup?email={email}")
    client.delete(f"/activities/Programming Class/signup?email={email}")


def test_unregister_removes_student_from_participants():
    """Test that unregistering removes the student from the activity's participants list"""
    email = "removetest@mergington.edu"
    activity_name = "Debate Team"

    client.post(f"/activities/{activity_name}/signup?email={email}")
    assert email in client.get("/activities").json()[activity_name]["participants"]

    client.delete(f"/activities/{activity_name}/signup?email={email}")
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_response_message_contains_email_and_activity():
    """Test that unregister response message contains email and activity name"""
    email = "unreg_msg@mergington.edu"
    activity_name = "Science Club"

    client.post(f"/activities/{activity_name}/signup?email={email}")
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 200
    data = response.json()
    assert email in data["message"]
    assert activity_name in data["message"]


def test_unregister_activity_name_case_sensitive():
    """Test that activity name matching is case-sensitive for unregister"""
    response = client.delete("/activities/chess club/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_get_skills_returns_list_type():
    """Test that the skills endpoint returns a JSON list, not a set"""
    email = "listcheck@mergington.edu"
    client.post(f"/activities/Drama Club/signup?email={email}")

    response = client.get(f"/skills/{email}")
    data = response.json()
    assert isinstance(data["skills"], list)

    client.delete(f"/activities/Drama Club/signup?email={email}")


def test_get_skills_returns_email_field():
    """Test that the skills endpoint response includes the queried email"""
    email = "emailfield@mergington.edu"

    response = client.get(f"/skills/{email}")
    assert response.status_code == 200
    assert response.json()["email"] == email


def test_get_skills_empty_list_for_student_with_no_activities():
    """Test that a student with no activity signups gets an empty skills list"""
    response = client.get("/skills/brandnew@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert data["skills"] == []


def test_get_skills_invalid_email_formats():
    """Test that various invalid email formats are rejected by the skills endpoint"""
    invalid_emails = [
        "notanemail",
        "missing@tld",
        "@nodomain.edu",
        "no-at-sign",
    ]
    for email in invalid_emails:
        response = client.get(f"/skills/{email}")
        assert response.status_code == 400, f"Email '{email}' should be rejected"
        assert "Invalid email format" in response.json()["detail"]