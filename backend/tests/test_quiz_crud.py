"""Quiz creation, editing, deletion, and the ownership boundary between users."""
from conftest import register_and_login, create_quiz, create_published_quiz, quiz_payload


def test_create_quiz_returns_nested_questions_and_answers(client):
    register_and_login(client)
    quiz = create_quiz(client)
    assert quiz["title"] == "Capitals"
    assert quiz["isPublished"] is False
    assert quiz["share_link"] is None
    assert len(quiz["questions"]) == 2
    assert len(quiz["questions"][0]["answers"]) == 2


def test_create_quiz_requires_authentication(client):
    response = client.post("/api/quizzes", json=quiz_payload())
    assert response.status_code == 401


def test_listing_quizzes_requires_authentication(client):
    assert client.get("/api/quizzes").status_code == 401


def test_quiz_list_only_contains_your_own_quizzes(client, second_client):
    register_and_login(client, email="owner@example.com")
    create_quiz(client, title="Mine")

    register_and_login(second_client, email="other@example.com", display_name="Other")
    create_quiz(second_client, title="Theirs")

    titles = [q["title"] for q in client.get("/api/quizzes").json()]
    assert titles == ["Mine"]


def test_non_owner_cannot_read_a_quiz(client, second_client):
    register_and_login(client, email="owner@example.com")
    quiz = create_quiz(client)

    register_and_login(second_client, email="other@example.com", display_name="Other")
    response = second_client.get(f"/api/quizzes/{quiz['id']}")
    assert response.status_code == 403


def test_non_owner_cannot_edit_a_quiz(client, second_client):
    register_and_login(client, email="owner@example.com")
    quiz = create_quiz(client)

    register_and_login(second_client, email="other@example.com", display_name="Other")
    response = second_client.patch(f"/api/quizzes/{quiz['id']}",
                                   json=quiz_payload(title="Hijacked"))
    assert response.status_code == 403


def test_non_owner_cannot_delete_a_quiz(client, second_client):
    register_and_login(client, email="owner@example.com")
    quiz = create_quiz(client)

    register_and_login(second_client, email="other@example.com", display_name="Other")
    assert second_client.delete(f"/api/quizzes/{quiz['id']}").status_code == 403


def test_reading_a_missing_quiz_returns_404(client):
    register_and_login(client)
    assert client.get("/api/quizzes/9999").status_code == 404


def test_editing_replaces_questions(client):
    register_and_login(client)
    quiz = create_quiz(client)
    response = client.patch(f"/api/quizzes/{quiz['id']}", json=quiz_payload(
        title="Rewritten",
        questions=[{
            "prompt": "Only question now?",
            "answers": [
                {"text": "Yes", "isCorrect": True},
                {"text": "No", "isCorrect": False},
            ],
        }],
    ))
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Rewritten"
    assert len(body["questions"]) == 1


def test_unpublished_quiz_can_be_deleted(client):
    register_and_login(client)
    quiz = create_quiz(client)
    assert client.delete(f"/api/quizzes/{quiz['id']}").status_code == 204
    assert client.get(f"/api/quizzes/{quiz['id']}").status_code == 404


def test_published_quiz_cannot_be_edited(client):
    register_and_login(client)
    quiz = create_published_quiz(client)
    response = client.patch(f"/api/quizzes/{quiz['id']}", json=quiz_payload(title="Sneaky"))
    assert response.status_code in (401, 409)


def test_published_quiz_cannot_be_deleted(client):
    register_and_login(client)
    quiz = create_published_quiz(client)
    assert client.delete(f"/api/quizzes/{quiz['id']}").status_code in (401, 409)
