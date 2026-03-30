@@ -205,3 +205,250 @@
     response = client.delete("/activities/Chess Club/signup?email=invalid-email")
     assert response.status_code == 400
     assert "Invalid email format" in response.json()["detail"]
+
+
+# --- signup_for_activity: message format ---
+
+def test_signup_response_message_format():
+    """Test that signup returns the correct message format"""
+    email = "msgformat@mergington.edu"
+    response = client.post(f"/activities/Chess Club/signup?email={email}")
+    assert response.status_code == 200
+    assert response.json()["message"] == f"Signed up {email} for Chess Club"
+    client.delete(f"/activities/Chess Club/signup?email={email}")
+
+
+# --- signup_for_activity: participants list updated ---
+
+def test_signup_adds_to_participants_list():
+    """Test that signing up adds the student to the activity participants list"""
+    email = "participant_check@mergington.edu"
+    activity_name = "Swimming Club"
+
+    before = client.get("/activities").json()[activity_name]["participants"]
+    assert email not in before
+
+    client.post(f"/activities/{activity_name}/signup?email={email}")
+
+    after = client.get("/activities").json()[activity_name]["participants"]
+    assert email in after
+    assert len(after) == len(before) + 1
+
+    client.delete(f"/activities/{activity_name}/signup?email={email}")
+
+
+# --- signup_for_activity: skills are granted ---
+
+def test_signup_grants_activity_skills():
+    """Test that signing up grants the student skills from the activity"""
+    email = "newskills@mergington.edu"
+
+    # Ensure student has no prior skills
+    assert client.get(f"/skills/{email}").json()["skills"] == []
+
+    client.post(f"/activities/Drama Club/signup?email={email}")
+
+    skills = set(client.get(f"/skills/{email}").json()["skills"])
+    expected_skills = {"Public Speaking", "Confidence", "Creativity", "Teamwork"}
+    assert expected_skills == skills
+
+    client.delete(f"/activities/Drama Club/signup?email={email}")
+
+
+# --- signup_for_activity: skills accumulate across multiple activities ---
+
+def test_signup_skills_accumulate_across_activities():
+    """Test that skills from multiple activities are unioned together"""
+    email = "skillaccum@mergington.edu"
+
+    client.post(f"/activities/Programming Class/signup?email={email}")
+    skills_after_first = set(client.get(f"/skills/{email}").json()["skills"])
+    assert skills_after_first == {"Coding", "Problem Solving", "Logical Thinking", "Debugging"}
+
+    client.post(f"/activities/Chess Club/signup?email={email}")
+    skills_after_second = set(client.get(f"/skills/{email}").json()["skills"])
+
+    # Should contain skills from both activities
+    assert skills_after_first.issubset(skills_after_second)
+    assert "Strategic Thinking" in skills_after_second
+    assert "Critical Analysis" in skills_after_second
+    assert len(skills_after_second) > len(skills_after_first)
+
+    client.delete(f"/activities/Programming Class/signup?email={email}")
+    client.delete(f"/activities/Chess Club/signup?email={email}")
+
+
+# --- signup_for_activity: skills are not duplicated ---
+
+def test_signup_shared_skills_not_duplicated():
+    """Test that overlapping skills are not duplicated when signing up for multiple activities"""
+    email = "nodupskills@mergington.edu"
+
+    # Both Chess Club and Programming Class have "Problem Solving"
+    client.post(f"/activities/Chess Club/signup?email={email}")
+    client.post(f"/activities/Programming Class/signup?email={email}")
+
+    skills = client.get(f"/skills/{email}").json()["skills"]
+    assert skills.count("Problem Solving") == 1
+
+    client.delete(f"/activities/Chess Club/signup?email={email}")
+    client.delete(f"/activities/Programming Class/signup?email={email}")
+
+
+# --- signup_for_activity: invalid email edge cases ---
+
+def test_signup_invalid_email_formats():
+    """Test various invalid email formats are rejected by signup"""
+    invalid_emails = [
+        "invalid",
+        "@mergington.edu",
+        "test@",
+        "test@@mergington.edu",
+        "test@mergington",
+        "",
+        "test@.edu",
+    ]
+    for email in invalid_emails:
+        response = client.post(f"/activities/Chess Club/signup?email={email}")
+        assert response.status_code == 400, f"Expected 400 for email '{email}'"
+        assert "Invalid email format" in response.json()["detail"]
+
+
+# --- signup_for_activity: valid email edge cases ---
+
+def test_signup_valid_email_formats():
+    """Test various valid email formats are accepted by signup"""
+    import urllib.parse
+
+    valid_emails = [
+        "test.name@mergington.edu",
+        "test_underscore@mergington.edu",
+        "123numeric@mergington.edu",
+        "test@sub.mergington.edu",
+    ]
+    for email in valid_emails:
+        encoded = urllib.parse.quote(email, safe="@")
+        response = client.post(f"/activities/Art Studio/signup?email={encoded}")
+        assert response.status_code == 200, f"Expected 200 for email '{email}'"
+        client.delete(f"/activities/Art Studio/signup?email={encoded}")
+
+
+# --- signup_for_activity: case-sensitive activity names ---
+
+def test_signup_case_sensitive_activity_name():
+    """Test that activity lookup is case-sensitive"""
+    response = client.post("/activities/chess club/signup?email=case@mergington.edu")
+    assert response.status_code == 404
+    assert "Activity not found" in response.json()["detail"]
+
+
+# --- signup_for_activity: multiple students same activity ---
+
+def test_signup_multiple_students_same_activity():
+    """Test that multiple students can sign up for the same activity"""
+    activity_name = "Debate Team"
+    emails = ["debater1@mergington.edu", "debater2@mergington.edu", "debater3@mergington.edu"]
+
+    for email in emails:
+        response = client.post(f"/activities/{activity_name}/signup?email={email}")
+        assert response.status_code == 200
+
+    participants = client.get("/activities").json()[activity_name]["participants"]
+    for email in emails:
+        assert email in participants
+
+    for email in emails:
+        client.delete(f"/activities/{activity_name}/signup?email={email}")
+
+
+# --- unregister_from_activity: message format ---
+
+def test_unregister_response_message_format():
+    """Test that unregister returns the correct message format"""
+    email = "unreg_msg@mergington.edu"
+    client.post(f"/activities/Chess Club/signup?email={email}")
+    response = client.delete(f"/activities/Chess Club/signup?email={email}")
+    assert response.status_code == 200
+    assert response.json()["message"] == f"Unregistered {email} from Chess Club"
+
+
+# --- unregister_from_activity: removes from participants list ---
+
+def test_unregister_removes_from_participants_list():
+    """Test that unregistering removes the student from the activity participants list"""
+    email = "removeme@mergington.edu"
+    activity_name = "Science Club"
+
+    client.post(f"/activities/{activity_name}/signup?email={email}")
+    assert email in client.get("/activities").json()[activity_name]["participants"]
+
+    client.delete(f"/activities/{activity_name}/signup?email={email}")
+    assert email not in client.get("/activities").json()[activity_name]["participants"]
+
+
+# --- unregister_from_activity: skills retained after unregister ---
+
+def test_unregister_does_not_remove_skills():
+    """Test that skills gained from an activity are retained after unregistering"""
+    email = "retainskills@mergington.edu"
+
+    client.post(f"/activities/Science Club/signup?email={email}")
+    skills_before = set(client.get(f"/skills/{email}").json()["skills"])
+    assert len(skills_before) > 0
+
+    client.delete(f"/activities/Science Club/signup?email={email}")
+    skills_after = set(client.get(f"/skills/{email}").json()["skills"])
+
+    assert skills_before == skills_after
+
+
+# --- unregister_from_activity: invalid email edge cases ---
+
+def test_unregister_invalid_email_formats():
+    """Test various invalid email formats are rejected by unregister"""
+    invalid_emails = [
+        "invalid",
+        "@mergington.edu",
+        "test@",
+        "test@@mergington.edu",
+        "test@mergington",
+        "",
+    ]
+    for email in invalid_emails:
+        response = client.delete(f"/activities/Chess Club/signup?email={email}")
+        assert response.status_code == 400, f"Expected 400 for email '{email}'"
+        assert "Invalid email format" in response.json()["detail"]
+
+
+# --- unregister_from_activity: case-sensitive activity names ---
+
+def test_unregister_case_sensitive_activity_name():
+    """Test that unregister activity lookup is case-sensitive"""
+    response = client.delete("/activities/chess club/signup?email=case@mergington.edu")
+    assert response.status_code == 404
+    assert "Activity not found" in response.json()["detail"]
+
+
+# --- signup_for_activity: activity name with spaces ---
+
+def test_signup_activity_name_with_spaces():
+    """Test that activity names with spaces are handled correctly in URL path"""
+    response = client.post("/activities/Chess Club/signup?email=spacename@mergington.edu")
+    assert response.status_code == 200
+    client.delete("/activities/Chess Club/signup?email=spacename@mergington.edu")
+
+
+# --- signup_for_activity + unregister: participant count consistency ---
+
+def test_signup_unregister_participant_count_consistency():
+    """Test that participant count is correctly maintained through signup and unregister"""
+    email = "countcheck@mergington.edu"
+    activity_name = "Basketball Team"
+
+    initial_count = len(client.get("/activities").json()[activity_name]["participants"])
+
+    client.post(f"/activities/{activity_name}/signup?email={email}")
+    assert len(client.get("/activities").json()[activity_name]["participants"]) == initial_count + 1
+
+    client.delete(f"/activities/{activity_name}/signup?email={email}")
+    assert len(client.get("/activities").json()[activity_name]["participants"]) == initial_count
