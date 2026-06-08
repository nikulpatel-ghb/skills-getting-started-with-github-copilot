"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
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


def get_default_activities() -> dict:
    """Get a fresh copy of the default activities database"""
    return {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Practice team play and compete in intramural soccer matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["alex@mergington.edu", "maria@mergington.edu"]
    },
    "Swimming Club": {
        "description": "Swim laps and learn advanced aquatic techniques",
        "schedule": "Wednesdays and Fridays, 3:00 PM - 4:30 PM",
        "max_participants": 16,
        "participants": ["nina@mergington.edu", "ethan@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore drawing, painting, and mixed media art projects",
        "schedule": "Mondays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["sophia@mergington.edu", "lily@mergington.edu"]
    },
    "Drama Club": {
        "description": "Practice acting, stagecraft, and prepare for school performances",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["jack@mergington.edu", "maya@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging math problems and prepare for competitions",
        "schedule": "Wednesdays, 4:00 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["julia@mergington.edu", "owen@mergington.edu"]
    },
    "Robotics Team": {
        "description": "Design, build, and program robots for science fairs and competitions",
        "schedule": "Mondays and Fridays, 3:30 PM - 5:30 PM",
        "max_participants": 14,
        "participants": ["liam@mergington.edu", "zoe@mergington.edu"]
    }
    }


# Global activities database instance
activities = get_default_activities()


def get_activities_db() -> dict:
    """Dependency that provides access to the activities database"""
    return activities


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities_endpoint(db: dict = Depends(get_activities_db)):
    return db


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, db: dict = Depends(get_activities_db)):
    """Sign up a student for an activity"""
    if activity_name not in db:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = db[activity_name]

    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up for this activity"
        )

    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}
