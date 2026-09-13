##*********Authentication section(registerIn, loginIn, userOut) request/response data
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

#request data
class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    display_name: str
    model_config = ConfigDict(from_attributes=True)
#request data
class LoginIn(BaseModel):
    email: EmailStr
    password: str
    model_config = ConfigDict(from_attributes=True)
#response data
class UserOut(BaseModel):
    id: int
    email: EmailStr
    display_name: str
    model_config = ConfigDict(from_attributes=True)

#schemas for the quiz endpoints-- 
# just the quiz dashboard to click a quick
class QuizOut(BaseModel):
    id: int
    title: str
    created_at: datetime
    description: str
    isPublished: bool
    model_config = ConfigDict(from_attributes=True)
#getting the answer for a question-response
class AnswerOut(BaseModel):
    id: int
    text: str
    orderIndex: int
    isCorrect: bool
    model_config = ConfigDict(from_attributes=True)
#getting the questions from a quiz-- looking at a certain quiz
class QuestionsOut(BaseModel):
    id: int
    prompt: str
    answers: list[AnswerOut]
    orderIndex: int
    model_config = ConfigDict(from_attributes=True)
#for editing the quiz gives all info
class QuizEditorOut(BaseModel):
    id: int
    created_at: datetime
    title: str
    questions: list[QuestionsOut]
    description: str
    isPublished: bool
    model_config = ConfigDict(from_attributes=True)
#for taking in answer data for each question
class AnswerIn(BaseModel):
    text: str
    isCorrect: bool
#for taking in the question data
class QuestionIn(BaseModel):
    prompt: str
    answers: list[AnswerIn]
#for taking in quiz data-- what is sent from the user when the submit a creation. This will be single shot creation so it takes questions, answers, and description because will have user fill out form in frontend
class QuizCreateIn(BaseModel):
    title: str
    description: str
    questions: list[QuestionIn]




