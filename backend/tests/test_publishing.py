"""Publishing is the gate that turns a draft into something takeable.

Each of these validations exists so a broken quiz can never reach a taker.
"""
from conftest import register_and_login, create_quiz, quiz_payload


def one_question(answers):
    return [{"prompt": "A question?", "answers": answers}]


def test_cannot_publish_a_quiz_with_no_questions(client):
    register_and_login(client)
    quiz = create_quiz(client, questions=[])
    response = client.post(f"/api/quizzes/{quiz['id']}/publish")
    assert response.status_code == 400


def test_cannot_publish_a_question_with_only_one_answer(client):
    register_and_login(client)
    quiz = create_quiz(client, questions=one_question([
        {"text": "Lonely", "isCorrect": True},
    ]))
    response = client.post(f"/api/quizzes/{quiz['id']}/publish")
    assert response.status_code == 400


def test_cannot_publish_a_question_with_two_correct_answers(client):
    register_and_login(client)
    quiz = create_quiz(client, questions=one_question([
        {"text": "Right", "isCorrect": True},
        {"text": "Also right", "isCorrect": True},
    ]))
    response = client.post(f"/api/quizzes/{quiz['id']}/publish")
    assert response.status_code == 400


def test_cannot_publish_a_question_with_no_correct_answer(client):
    register_and_login(client)
    quiz = create_quiz(client, questions=one_question([
        {"text": "Wrong", "isCorrect": False},
        {"text": "Also wrong", "isCorrect": False},
    ]))
    response = client.post(f"/api/quizzes/{quiz['id']}/publish")
    assert response.status_code == 400


def test_failed_publish_leaves_the_quiz_unpublished(client):
    register_and_login(client)
    quiz = create_quiz(client, questions=[])
    client.post(f"/api/quizzes/{quiz['id']}/publish")
    after = client.get(f"/api/quizzes/{quiz['id']}").json()
    assert after["isPublished"] is False
    assert after["share_link"] is None


def test_publishing_a_valid_quiz_issues_a_share_link(client):
    register_and_login(client)
    quiz = create_quiz(client)
    response = client.post(f"/api/quizzes/{quiz['id']}/publish")
    assert response.status_code == 200
    body = response.json()
    assert body["isPublished"] is True
    assert body["share_link"]


def test_publishing_twice_is_a_conflict(client):
    register_and_login(client)
    quiz = create_quiz(client)
    client.post(f"/api/quizzes/{quiz['id']}/publish")
    second = client.post(f"/api/quizzes/{quiz['id']}/publish")
    assert second.status_code == 409


def test_non_owner_cannot_publish(client, second_client):
    register_and_login(client, email="owner@example.com")
    quiz = create_quiz(client)

    register_and_login(second_client, email="other@example.com", display_name="Other")
    response = second_client.post(f"/api/quizzes/{quiz['id']}/publish")
    assert response.status_code == 403
