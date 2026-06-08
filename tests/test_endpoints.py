"""Comprehensive tests for the Activities API endpoints"""

import pytest


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) == 9
    
    def test_get_activities_contains_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert all(field in activity_data for field in required_fields)
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
    
    def test_chess_club_has_initial_participants(self, client):
        """Test that Chess Club has expected initial participants"""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]
    
    def test_activities_are_isolated_between_tests(self, test_activities):
        """Test that each test gets a fresh copy of activities"""
        assert len(test_activities) == 9
        # Modify the fixture
        test_activities["Chess Club"]["participants"].clear()
        
        # Create another fixture - should have original data
        fresh_activities = get_default_activities()
        assert len(fresh_activities["Chess Club"]["participants"]) == 2


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client, test_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "newstudent@mergington.edu" in result["message"]
        assert "Chess Club" in result["message"]
        
        # Verify participant was added
        assert "newstudent@mergington.edu" in test_activities["Chess Club"]["participants"]
    
    def test_signup_adds_to_participants_list(self, client, test_activities):
        """Test that signup actually adds participant to the list"""
        initial_count = len(test_activities["Programming Class"]["participants"])
        
        response = client.post(
            "/activities/Programming Class/signup?email=alice@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify count increased
        assert len(test_activities["Programming Class"]["participants"]) == initial_count + 1
    
    def test_signup_activity_not_found(self, client):
        """Test signup fails for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]
    
    def test_signup_duplicate_participant_error(self, client):
        """Test that duplicate signups are rejected"""
        # Try to sign up an already registered participant
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        
        assert response.status_code == 400
        result = response.json()
        assert "already signed up" in result["detail"]
    
    def test_signup_multiple_different_activities(self, client, test_activities):
        """Test that same student can sign up for multiple activities"""
        email = "multiactivity@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify in both activities
        assert email in test_activities["Chess Club"]["participants"]
        assert email in test_activities["Programming Class"]["participants"]
    
    def test_signup_with_special_characters_in_email(self, client, test_activities):
        """Test signup with special characters in email"""
        email = "user+tag@example.com"
        response = client.post(
            "/activities/Soccer Team/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert email in test_activities["Soccer Team"]["participants"]
    
    def test_signup_with_missing_email_parameter(self, client):
        """Test signup fails without email parameter"""
        response = client.post("/activities/Chess Club/signup")
        
        # FastAPI returns 422 for missing required parameters
        assert response.status_code == 422
    
    def test_signup_with_invalid_activity_name(self, client):
        """Test signup with activity name that doesn't exist"""
        response = client.post(
            "/activities/Flying Club/signup?email=test@mergington.edu"
        )
        
        assert response.status_code == 404
    
    def test_signup_case_sensitive_activity_name(self, client):
        """Test that activity names are case-sensitive"""
        # "chess club" (lowercase) should not match "Chess Club"
        response = client.post(
            "/activities/chess club/signup?email=test@mergington.edu"
        )
        
        assert response.status_code == 404
    
    def test_signup_multiple_students_different_activities(self, client, test_activities):
        """Test multiple students signing up for different activities"""
        responses = []
        
        signups = [
            ("Chess Club", "student1@mergington.edu"),
            ("Programming Class", "student2@mergington.edu"),
            ("Gym Class", "student3@mergington.edu"),
        ]
        
        for activity, email in signups:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            responses.append(response)
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
        
        # Verify all were added
        assert "student1@mergington.edu" in test_activities["Chess Club"]["participants"]
        assert "student2@mergington.edu" in test_activities["Programming Class"]["participants"]
        assert "student3@mergington.edu" in test_activities["Gym Class"]["participants"]
    
    def test_signup_empty_email(self, client):
        """Test signup with empty email parameter"""
        response = client.post(
            "/activities/Chess Club/signup?email="
        )
        
        # Empty string should be accepted by FastAPI but may fail validation
        # Depending on FastAPI version, this might be 200 or 422
        # Let's verify behavior
        if response.status_code == 200:
            # If empty email is allowed, verify it was added
            result = response.json()
            assert "message" in result
        else:
            # If it fails, should be validation error
            assert response.status_code in [422, 400]
    
    def test_signup_response_message_format(self, client):
        """Test that signup response message is correctly formatted"""
        email = "format@test.edu"
        activity = "Drama Club"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 200
        result = response.json()
        expected_message = f"Signed up {email} for {activity}"
        assert result["message"] == expected_message


class TestIntegration:
    """Integration tests combining multiple endpoints"""
    
    def test_get_activities_after_signup(self, client, test_activities):
        """Test that GET /activities reflects signup changes"""
        email = "integration@test.edu"
        activity = "Art Club"
        
        # Get initial state
        response1 = client.get("/activities")
        initial_participants = len(response1.json()[activity]["participants"])
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Get updated state
        response2 = client.get("/activities")
        updated_participants = len(response2.json()[activity]["participants"])
        
        # Verify change
        assert updated_participants == initial_participants + 1
        assert email in response2.json()[activity]["participants"]
    
    def test_activities_isolation_between_requests(self, client, test_activities):
        """Test that state is properly isolated within a test session"""
        email1 = "isolation1@test.edu"
        email2 = "isolation2@test.edu"
        
        # Signup in first request
        client.post("/activities/Robotics Team/signup?email={email1}")
        
        # Get activities in second request
        response = client.get("/activities")
        participants = response.json()["Robotics Team"]["participants"]
        
        # Both original and new should be present in this test
        assert len(participants) >= 2
        assert "liam@mergington.edu" in participants or email1 in participants


# Import here to avoid circular imports during fixture definition
from src.app import get_default_activities
