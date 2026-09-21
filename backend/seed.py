"""Fills the database with mock quizzes so the pages have something to show.

    python seed.py                  -> seeds demo@example.com (created if missing, password: demo1234)
    python seed.py you@example.com  -> seeds an account you already signed up with

Re-running replaces the seeded quizzes instead of piling up duplicates, so it is
safe to run as often as you like. Only quizzes with the mock titles are touched.
"""
import secrets
import sys

import bcrypt
from sqlalchemy import select

from database import Base, engine, sessionLocal
from models import User, Quiz, Question, Answer, Attempt, AnswerAttempt

DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "demo1234"
DEMO_NAME = "Demo User"

#each quiz is (title, description, published, questions), and a question is
#(prompt, [answers]) where the first answer listed is the correct one
MOCK_QUIZZES = [
    (
        "General Knowledge",
        "A quick five question warm up covering a bit of everything.",
        True,
        [
            ("What is the capital of Australia?", ["Canberra", "Sydney", "Melbourne", "Perth"]),
            ("How many continents are there?", ["Seven", "Five", "Six", "Eight"]),
            ("Which planet is closest to the sun?", ["Mercury", "Venus", "Mars", "Earth"]),
            ("What is the largest ocean on Earth?", ["Pacific", "Atlantic", "Indian", "Arctic"]),
            ("How many minutes are in a full day?", ["1440", "720", "2400", "960"]),
        ],
    ),
    (
        "World Geography",
        "Capitals, rivers and borders. Harder than it looks.",
        True,
        [
            ("Which river runs through Cairo?", ["The Nile", "The Congo", "The Amazon", "The Danube"]),
            ("Mount Everest sits on the border of Nepal and which country?", ["China", "India", "Bhutan", "Pakistan"]),
            ("What is the smallest country in the world?", ["Vatican City", "Monaco", "San Marino", "Malta"]),
            ("Which country has the most time zones?", ["France", "Russia", "United States", "Canada"]),
        ],
    ),
    (
        "JavaScript Basics",
        "Fundamentals every frontend developer should have down.",
        True,
        [
            ("What does '===' compare?", ["Value and type", "Value only", "Type only", "Reference only"]),
            ("Which method adds an item to the end of an array?", ["push()", "shift()", "unshift()", "pop()"]),
            ("What does 'const' prevent?", ["Reassigning the binding", "Mutating an object", "Hoisting", "Shadowing"]),
            ("What is typeof null?", ["'object'", "'null'", "'undefined'", "'boolean'"]),
        ],
    ),
    (
        "Space and Astronomy",
        "Still being written. Publish it once the questions are finished.",
        False,
        [
            ("Which planet has the most moons?", ["Saturn", "Jupiter", "Neptune", "Uranus"]),
            ("What galaxy is Earth in?", ["The Milky Way", "Andromeda", "Triangulum", "Whirlpool"]),
            ("How long does sunlight take to reach Earth?", ["About 8 minutes", "About 8 seconds", "About an hour", "Instantly"]),
        ],
    ),
    (
        "Movie Trivia",
        "A draft quiz for movie night. No questions written yet.",
        False,
        [],
    ),
]

#takers to put on every published quiz's leaderboard, best first
MOCK_TAKERS = ["alex", "jordan", "sam", "riley", "casey"]


def get_or_create_user(db, email):
    user = db.scalar(select(User).where(User.email == email.lower()))
    if user:
        return user, False
    user = User(
        email=email.lower(),
        password_hash=bcrypt.hashpw(DEMO_PASSWORD.encode(), bcrypt.gensalt()).decode(),
        display_name=DEMO_NAME,
    )
    db.add(user)
    db.flush()
    return user, True


def build_quiz(owner_id, title, description, published, questions):
    quiz = Quiz(owner_id=owner_id, title=title, description=description)
    for qIndex, (prompt, answers) in enumerate(questions):
        question = Question(prompt=prompt, orderIndex=qIndex)
        for aIndex, text in enumerate(answers):
            question.answers.append(Answer(text=text, isCorrect=(aIndex == 0), orderIndex=aIndex))
        quiz.questions.append(question)
    if published:
        quiz.isPublished = True
        quiz.share_link = secrets.token_urlsafe(8)
    return quiz


def add_attempts(quiz):
    """Gives a published quiz a leaderboard so the results page is not empty."""
    total = len(quiz.questions)
    for rank, display_name in enumerate(MOCK_TAKERS):
        #each taker drops one mark below the last, so the board spreads out
        #whether the quiz has three questions or ten
        correctCount = max(total - rank, 0)
        attempt = Attempt(
            display_name=display_name,
            score=correctCount,
            percentage_right=round(correctCount / total * 100) if total else 0,
        )
        for index, question in enumerate(quiz.questions):
            #the first answer is the correct one, so anything past the score is a wrong pick
            answer = question.answers[0] if index < correctCount else question.answers[-1]
            attempt.answers.append(AnswerAttempt(question_id=question.id, answer_id=answer.id))
        quiz.attempts.append(attempt)


def main():
    email = sys.argv[1] if len(sys.argv) > 1 else DEMO_EMAIL
    Base.metadata.create_all(bind=engine)
    db = sessionLocal()
    try:
        user, created = get_or_create_user(db, email)

        titles = [title for title, *_ in MOCK_QUIZZES]
        stale = db.scalars(select(Quiz).where(Quiz.owner_id == user.id, Quiz.title.in_(titles))).all()
        for quiz in stale:
            db.delete(quiz)
        db.flush()

        seeded = []
        for title, description, published, questions in MOCK_QUIZZES:
            quiz = build_quiz(user.id, title, description, published, questions)
            db.add(quiz)
            seeded.append(quiz)
        db.flush() #assigns the question and answer ids the attempts need to point at

        for quiz in seeded:
            if quiz.isPublished and quiz.questions:
                add_attempts(quiz)
        db.commit()

        print(f"Seeded {len(seeded)} quizzes for {user.email}" + (" (new account)" if created else ""))
        if created:
            print(f"  log in with {user.email} / {DEMO_PASSWORD}")
        if stale:
            print(f"  replaced {len(stale)} previously seeded quizzes")
        for quiz in seeded:
            state = f"published  /take/{quiz.share_link}" if quiz.isPublished else "draft"
            print(f"  {quiz.title:<22} {len(quiz.questions)} questions  {state}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
