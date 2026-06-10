import copy

import pytest
from fastapi.testclient import TestClient

from src import app

client = TestClient(app.app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(app.activities)
    yield
    app.activities.clear()
    app.activities.update(original_activities)


def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_for_activity_success():
    email = "newstudent@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in app.activities["Chess Club"]["participants"]


def test_signup_for_activity_duplicate():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_for_activity_not_found():
    response = client.post(
        "/activities/Nonexistent/signup",
        params={"email": "newstudent@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_success():
    email = "michael@mergington.edu"
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in app.activities["Chess Club"]["participants"]


def test_remove_participant_not_found():
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "nobody@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_participant_activity_not_found():
    response = client.delete(
        "/activities/Nonexistent/participants",
        params={"email": "newstudent@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
