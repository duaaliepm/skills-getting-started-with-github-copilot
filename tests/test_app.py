import copy
import pytest
from fastapi.testclient import TestClient
from src import app as myapp

@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(myapp.activities)
    yield
    myapp.activities = copy.deepcopy(original)

client = TestClient(myapp.app)


def test_root_redirect():
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (307, 302)
    assert resp.headers["location"] == "/static/index.html"


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_success():
    resp = client.post("/activities/Tennis%20Club/signup", params={"email": "new@mergington.edu"})
    assert resp.status_code == 200
    assert "Signed up new@mergington.edu for Tennis Club" in resp.json().get("message", "")
    assert "new@mergington.edu" in myapp.activities["Tennis Club"]["participants"]


def test_signup_duplicate():
    resp = client.post("/activities/Chess%20Club/signup", params={"email": "michael@mergington.edu"})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Student already signed up for this activity"


def test_unregister_success():
    resp = client.delete("/activities/Chess%20Club/participants", params={"email": "michael@mergington.edu"})
    assert resp.status_code == 200
    assert "Unregistered michael@mergington.edu from Chess Club" in resp.json().get("message", "")


def test_unregister_not_found():
    resp = client.delete("/activities/Chess%20Club/participants", params={"email": "nonexistent@mergington.edu"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Participant not found in this activity"
