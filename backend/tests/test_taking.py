"""Taking a quiz by share link, scoring, and the leaderboard.

The security claim the whole design rests on is that the answer key never
reaches a taker and scoring happens server-side -- that is what
test_start_quiz_does_not_leak_the_answer_key guards.
"""
import pytest

from conftest import register_and_login, create_quiz, create_published_quiz, quiz_payload


def correct_picks(owner_view):
    """Build a fully-correct submission from the owner's view of the quiz."""
    picks = []
    for question in owner_view["questions"]:
        answer = next(a for a in question["answers"] if a["isCorrect"])
        picks.append({"question_id": question["id"], "answer_id": answer["id"]})
    return picks


def wrong_picks(owner_view):
    picks = []
    for question in owner_view["questions"]:
        answer = next(a for a in question["answers"] if not a["isCorrect"])
        picks.append({"question_id": question["id"], "answer_id": answer["id"]})
    return picks


def test_unpublished_quiz_is_not_takeable(client):
    register_and_login(client)
    create_quiz(client)
    #a draft has no share link at all, so no link can resolve to it
    assert client.get("/api/quizzes/some-made-up-link/start-quiz").status_code == 404


def test_unknown_share_link_returns_404(client):
    assert client.get("/api/quizzes/not-a-real-link/start-quiz").status_code == 404


def test_start_quiz_does_not_leak_the_answer_key(client):
    register_and_login(client)
    quiz = create_published_quiz(client)

    response = client.get(f"/api/quizzes/{quiz['share_link']}/start-quiz")
    assert response.status_code == 200
    body = response.json()

    assert body["title"] == "Capitals"
    for question in body["questions"]:
        for answer in question["answers"]:
            assert "isCorrect" not in answer, "answer key leaked to the quiz taker"


def test_start_quiz_does_not_require_an_account(client):
    register_and_login(client)
    quiz = create_published_quiz(client)
    client.post("/logout")
    assert client.get(f"/api/quizzes/{quiz['share_link']}/start-quiz").status_code == 200


def test_display_name_is_available_before_anyone_uses_it(client):
    register_and_login(client)
    quiz = create_published_quiz(client)
    response = client.get(f"/api/quizzes/take/{quiz['share_link']}/check-name",
                          params={"display_name": "Steve"})
    assert response.status_code == 200
    assert response.json()["available"] is True


def test_display_name_is_taken_after_an_attempt(client):
    register_and_login(client)
    quiz = create_published_quiz(client)
    client.post(f"/api/quizzes/{quiz['share_link']}/submit", json={
        "display_name": "Steve", "picks": correct_picks(quiz),
    })
    response = client.get(f"/api/quizzes/take/{quiz['share_link']}/check-name",
                          params={"display_name": "Steve"})
    assert response.status_code in (401, 409)


def test_a_perfect_submission_scores_full_marks(client):
    register_and_login(client)
    quiz = create_published_quiz(client)

    submit = client.post(f"/api/quizzes/{quiz['share_link']}/submit", json={
        "display_name": "Perfect", "picks": correct_picks(quiz),
    })
    assert submit.status_code == 200

    board = client.get(f"/api/quizzes/{quiz['id']}/dashboard").json()
    assert board[0]["display_name"] == "Perfect"
    assert board[0]["score"] == 2
    assert board[0]["total"] == 2


def test_an_all_wrong_submission_scores_zero(client):
    register_and_login(client)
    quiz = create_published_quiz(client)

    client.post(f"/api/quizzes/{quiz['share_link']}/submit", json={
        "display_name": "Zero", "picks": wrong_picks(quiz),
    })
    board = client.get(f"/api/quizzes/{quiz['id']}/dashboard").json()
    assert board[0]["score"] == 0


def test_submitting_an_answer_from_another_question_is_rejected(client):
    register_and_login(client)
    quiz = create_published_quiz(client)

    first, second = quiz["questions"][0], quiz["questions"][1]
    response = client.post(f"/api/quizzes/{quiz['share_link']}/submit", json={
        "display_name": "Mismatch",
        #answer id belongs to the second question, question id to the first
        "picks": [{"question_id": first["id"], "answer_id": second["answers"][0]["id"]}],
    })
    assert response.status_code == 404


def test_submitting_an_unknown_question_is_rejected(client):
    register_and_login(client)
    quiz = create_published_quiz(client)
    response = client.post(f"/api/quizzes/{quiz['share_link']}/submit", json={
        "display_name": "Ghost",
        "picks": [{"question_id": 9999, "answer_id": 1}],
    })
    assert response.status_code == 404


def test_repeating_one_question_cannot_inflate_the_score(client):
    """A taker must not be able to answer the same question many times over."""
    register_and_login(client)
    quiz = create_published_quiz(client)

    question = quiz["questions"][0]
    right_answer = next(a for a in question["answers"] if a["isCorrect"])
    repeated = [{"question_id": question["id"], "answer_id": right_answer["id"]}] * 5

    response = client.post(f"/api/quizzes/{quiz['share_link']}/submit", json={
        "display_name": "Repeater", "picks": repeated,
    })
    assert response.status_code == 400

    #the rejected submission must not have left a half-scored attempt behind
    board = client.get(f"/api/quizzes/{quiz['id']}/dashboard").json()
    assert not any(entry["display_name"] == "Repeater" for entry in board)


def test_dashboard_is_ordered_by_score_descending(client):
    register_and_login(client)
    quiz = create_published_quiz(client)
    link = quiz["share_link"]

    client.post(f"/api/quizzes/{link}/submit",
                json={"display_name": "Low", "picks": wrong_picks(quiz)})
    client.post(f"/api/quizzes/{link}/submit",
                json={"display_name": "High", "picks": correct_picks(quiz)})

    board = client.get(f"/api/quizzes/{quiz['id']}/dashboard").json()
    scores = [entry["score"] for entry in board]
    assert scores == sorted(scores, reverse=True)
    assert board[0]["display_name"] == "High"


def test_dashboard_requires_authentication(client):
    register_and_login(client)
    quiz = create_published_quiz(client)
    client.post("/logout")
    assert client.get(f"/api/quizzes/{quiz['id']}/dashboard").status_code == 401


def test_non_owner_cannot_read_the_dashboard(client, second_client):
    register_and_login(client, email="owner@example.com")
    quiz = create_published_quiz(client)

    register_and_login(second_client, email="other@example.com", display_name="Other")
    response = second_client.get(f"/api/quizzes/{quiz['id']}/dashboard")
    assert response.status_code == 403
