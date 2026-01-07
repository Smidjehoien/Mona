"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        "skills": ["Strategic Thinking", "Problem Solving", "Critical Analysis"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        "skills": ["Coding", "Problem Solving", "Logical Thinking", "Debugging"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        "skills": ["Teamwork", "Physical Fitness", "Coordination"]
    }
}

# In-memory student skills database
student_skills = {
    "michael@mergington.edu": ["Strategic Thinking", "Problem Solving", "Critical Analysis"],
    "daniel@mergington.edu": ["Strategic Thinking", "Problem Solving", "Critical Analysis"],
    "emma@mergington.edu": ["Coding", "Problem Solving", "Logical Thinking", "Debugging"],
    "sophia@mergington.edu": ["Coding", "Problem Solving", "Logical Thinking", "Debugging"],
    "john@mergington.edu": ["Teamwork", "Physical Fitness", "Coordination"],
    "olivia@mergington.edu": ["Teamwork", "Physical Fitness", "Coordination"]
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Add student
    activity["participants"].append(email)
    
    # Update student skills
    if email not in student_skills:
        student_skills[email] = []
    
    # Add new skills from the activity
    for skill in activity.get("skills", []):
        if skill not in student_skills[email]:
            student_skills[email].append(skill)
    
    return {"message": f"Signed up {email} for {activity_name}"}


@app.get("/skills/{email}")
def get_student_skills(email: str):
    """Get skills for a specific student"""
    if email not in student_skills:
        return {"email": email, "skills": []}
    return {"email": email, "skills": student_skills[email]}
