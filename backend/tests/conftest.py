"""Shared test fixtures.

Every test runs against a fresh in-memory SQLite database, so the real
database.db is never touched and tests can't leak state into each other.
"""
import os
import sys
from pathlib import Path

#the app uses flat imports (from database import ...), so backend/ has to be importable
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

#these must be set before config.py is imported -- env vars outrank the .env file in
#pydantic-settings, which keeps the real DATABASE_URL from being picked up
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SESSION_SECRET"] = "test-secret-not-used-in-production"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
import models  # noqa: F401  -- registers the tables on Base before create_all
from main import app


@pytest.fixture
def db_session():
    #StaticPool keeps every connection pointed at the same in-memory db; without it
    #each connection would get its own empty database
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def client(db_session):
    """An unauthenticated client wired to the test database."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def second_client(db_session):
    """A separate client with its own cookie jar, for authorization tests.

    Shares the same database as `client` so one user can try to reach the
    other's quizzes.
    """
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


# ── helpers ───────────────────────────────────────────────────────────────────

def register_and_login(test_client, email="owner@example.com", password="hunter2",
                       display_name="Owner"):
    """Sign a user up and log them in. The session cookie sticks to the client."""
    signup = test_client.post("/api/auth/signup", json={
        "email": email, "password": password, "display_name": display_name,
    })
    assert signup.status_code == 200, signup.text
    login = test_client.post("/api/auth/login", json={
        "email": email, "password": password,
    })
    assert login.status_code == 200, login.text
    return signup.json()


def quiz_payload(title="Capitals", description="Geography basics", questions=None):
    """A valid, publishable quiz body. Override `questions` to make it invalid."""
    if questions is None:
        questions = [
            {
                "prompt": "Capital of France?",
                "answers": [
                    {"text": "Paris", "isCorrect": True},
                    {"text": "Lyon", "isCorrect": False},
                ],
            },
            {
                "prompt": "Capital of Japan?",
                "answers": [
                    {"text": "Tokyo", "isCorrect": True},
                    {"text": "Osaka", "isCorrect": False},
                ],
            },
        ]
    return {"title": title, "description": description, "questions": questions}


def create_quiz(test_client, **kwargs):
    response = test_client.post("/api/quizzes", json=quiz_payload(**kwargs))
    assert response.status_code == 200, response.text
    return response.json()


def create_published_quiz(test_client, **kwargs):
    quiz = create_quiz(test_client, **kwargs)
    response = test_client.post(f"/api/quizzes/{quiz['id']}/publish")
    assert response.status_code == 200, response.text
    return response.json()
