from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from database import Base
from datetime import datetime, timezone

#user storage: id, email(this is login method), pwd hash, display_name, created_at
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    password_hash: Mapped[str] 
    display_name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    owned_quiz: Mapped[bool] = mapped_column(default=False)
    quizzes = relationship("Quiz")

## models for the quizzes (quiz, questions, answers)
class Quiz(Base):
    __tablename__ = "quizzes"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    title: Mapped[str]
    questions = relationship("Question", cascade="all, delete-orphan", order_by="Question.orderIndex")
    description: Mapped[str]
    isPublished: Mapped[bool] = mapped_column(default=False)
    share_link: Mapped[str | None]
class Question(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(primary_key=True)
    prompt: Mapped[str]
    quiz_id: Mapped[int] = mapped_column(ForeignKey('quizzes.id'))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    orderIndex: Mapped[int] = mapped_column(nullable=False, default=0)
    answers = relationship("Answer", cascade="all, delete-orphan", order_by="Answer.orderIndex")
class Answer(Base):
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    isCorrect: Mapped[bool] = mapped_column(default=False)
    orderIndex: Mapped[int] = mapped_column(default=0, nullable=False)





