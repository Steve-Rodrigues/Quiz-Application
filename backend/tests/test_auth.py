"""Signup, login, session handling."""
from conftest import register_and_login


def test_signup_returns_user_without_leaking_password(client):
    response = client.post("/api/auth/signup", json={
        "email": "new@example.com", "password": "hunter2", "display_name": "New",
    })
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "new@example.com"
    assert body["display_name"] == "New"
    assert "id" in body
    #the response schema must never carry the hash back to the client
    assert "password_hash" not in body
    assert "password" not in body


def test_signup_rejects_duplicate_email(client):
    payload = {"email": "dupe@example.com", "password": "hunter2", "display_name": "A"}
    assert client.post("/api/auth/signup", json=payload).status_code == 200
    second = client.post("/api/auth/signup", json=payload)
    assert second.status_code in (401, 409)


def test_signup_rejects_malformed_email(client):
    response = client.post("/api/auth/signup", json={
        "email": "not-an-email", "password": "hunter2", "display_name": "A",
    })
    assert response.status_code == 422


def test_login_with_wrong_password_is_rejected(client):
    client.post("/api/auth/signup", json={
        "email": "user@example.com", "password": "correct", "display_name": "U",
    })
    response = client.post("/api/auth/login", json={
        "email": "user@example.com", "password": "wrong",
    })
    assert response.status_code == 401


def test_login_with_unknown_email_is_rejected(client):
    response = client.post("/api/auth/login", json={
        "email": "ghost@example.com", "password": "whatever",
    })
    assert response.status_code in (401, 404)


def test_login_is_case_insensitive_on_email(client):
    client.post("/api/auth/signup", json={
        "email": "mixed@example.com", "password": "hunter2", "display_name": "M",
    })
    response = client.post("/api/auth/login", json={
        "email": "MIXED@example.com", "password": "hunter2",
    })
    assert response.status_code == 200


def test_me_requires_authentication(client):
    assert client.get("/me").status_code == 401


def test_me_returns_current_user_when_logged_in(client):
    user = register_and_login(client)
    response = client.get("/me")
    assert response.status_code == 200
    assert response.json()["id"] == user["id"]


def test_logout_invalidates_the_session(client):
    register_and_login(client)
    assert client.get("/me").status_code == 200
    assert client.post("/logout").status_code == 200
    assert client.get("/me").status_code == 401
