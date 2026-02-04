from fastapi.testclient import TestClient
from urllib.parse import quote

from src.app import app, activities

client = TestClient(app)


def setup_module(module):
    # snapshot activities to restore after tests
    module._activities_backup = {
        k: {
            "description": v["description"],
            "schedule": v["schedule"],
            "max_participants": v["max_participants"],
            "participants": list(v["participants"]),
        }
        for k, v in activities.items()
    }


def teardown_module(module):
    # restore original activities
    activities.clear()
    for k, v in module._activities_backup.items():
        activities[k] = {
            "description": v["description"],
            "schedule": v["schedule"],
            "max_participants": v["max_participants"],
            "participants": list(v["participants"]),
        }


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Soccer Team" in data


def test_signup_and_unregister():
    activity = "Chess Club"
    email = "test_student@example.com"

    # ensure clean state
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    path_signup = f"/activities/{quote(activity)}/signup"
    resp = client.post(path_signup, params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # now unregister
    path_delete = f"/activities/{quote(activity)}/participants"
    resp2 = client.delete(path_delete, params={"email": email})
    assert resp2.status_code == 200
    assert email not in activities[activity]["participants"]
