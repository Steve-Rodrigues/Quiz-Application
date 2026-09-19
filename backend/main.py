import secrets

from fastapi import FastAPI, Request, Depends, HTTPException, status
from database import Base, engine, get_db
from config import settings
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from schemas import RegisterIn, LoginIn, UserOut,QuizCreateIn, QuizEditorOut, QuizStartOut, QuestionsStartOut, AnswersStartOut, AttemptSubmitIn, AnswerPickIn, DashboardOut
from models import User, Quiz, Question, Answer, Attempt, AnswerAttempt
import bcrypt
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine) #create the tables on startup

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret) #the session middleware to check the sessions using the secret comparing to signature passed thorugh the header
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

#sign up route
@app.post('/api/auth/signup', response_model=UserOut)
def signUp(registerInfo: RegisterIn, db: Session = Depends(get_db)):
    userCheck = db.scalar(select(User).where(registerInfo.email == User.email))
    if userCheck: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User already exists")
    hashedPwd = bcrypt.hashpw(registerInfo.password.encode(), bcrypt.gensalt()).decode()
    user = User(email=registerInfo.email.lower(), password_hash=hashedPwd, display_name=registerInfo.display_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post('/api/auth/login', response_model=UserOut)
def login(loginInfo: LoginIn, request: Request, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == loginInfo.email.lower()))
    if not user: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    #verify the submitted password against the stored hash before handing out a session
    if not bcrypt.checkpw(loginInfo.password.encode(), user.password_hash.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    #login by signing and shipping the session to the browser with the cookie
    request.session["user_id"] = user.id
    return user

#get user dependancy for protected endpoints to see if the current user is still valid in the system
def get_curr_user(request: Request, db: Session = Depends(get_db)):
    isSession = request.session.get('user_id')
    if not isSession: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user attempt")
    user = db.scalar(select(User).where(User.id == isSession))
    if not user: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user attempt")
    return user #returns the user if there was a session meaning the user was validly logged on
@app.get('/me',response_model=UserOut)
def getMe(currUser: User = Depends(get_curr_user)):
    return currUser
@app.post('/logout')
def logout(request:Request):
    request.session.clear() #clears the browser session cookie so user is not valid anymore
    return {"Status": "Success"}

#quiz section
#owner check of the quiz dependency-- takes quiz id from route and checks if the quiz linked to that id is owned by the user trying to access it
def check_quiz_owner(quiz_id:int ,user: User = Depends(get_curr_user), db: Session = Depends(get_db)):
    quiz = db.scalar(select(Quiz).where(Quiz.id == quiz_id))
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found.")
    if quiz.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of this quiz.")
    return quiz

#endpoint to get quizzes created by current user
@app.get('/api/quizzes',response_model=list[QuizEditorOut])
def get_quizzes(user: User = Depends(get_curr_user), db: Session = Depends(get_db)):
    allQuizzes = db.scalars(select(Quiz).where(user.id == Quiz.owner_id)).all()
    return allQuizzes
#creating a quiz after user submits in the frontend code
@app.post('/api/quizzes',response_model=QuizEditorOut)
def createQuiz(body: QuizCreateIn ,user: User = Depends(get_curr_user), db: Session = Depends(get_db)):
    quiz = Quiz(owner_id=user.id,title=body.title, description=body.description)
    for qIndex, q in enumerate(body.questions):
        question = Question(prompt=q.prompt, orderIndex=qIndex)
        for aIndex, a in enumerate(q.answers):
            answer = Answer(text=a.text, isCorrect=a.isCorrect, orderIndex=aIndex)
            question.answers.append(answer)
        quiz.questions.append(question)
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz
#get the info for a quiz when the owner wants to inspect from dashboard page-- frontend builds the page with the data sent through this endpoint so include answer because it is gaurded by owner depenency
@app.get('/api/quizzes/{quiz_id}', response_model=QuizEditorOut)
def editQuiz(quiz: Quiz = Depends(check_quiz_owner)):
    return quiz
#allows OWNER to update his quiz before it is published-- need to check if the quiz is published or not before anything
@app.patch('/api/quizzes/{quiz_id}', response_model=QuizEditorOut)
def updateQuiz(body:QuizCreateIn,quiz: Quiz = Depends(check_quiz_owner), db: Session = Depends(get_db)):
    if quiz.isPublished:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Can not edit a quiz after publishing")
    quiz.title = body.title
    quiz.description = body.description
    quiz.questions.clear()
    for qIndex, q in enumerate(body.questions):
        question = Question(prompt=q.prompt, orderIndex=qIndex)
        for aIndex, a in enumerate(q.answers):
            answer = Answer(text=a.text, isCorrect=a.isCorrect, orderIndex=aIndex)
            question.answers.append(answer)
        quiz.questions.append(question)
    db.commit()
    db.refresh(quiz)
    return quiz
#delete endpoint-- can only delete a quiz if NOT published yet
@app.delete('/api/quizzes/{quiz_id}', status_code=status.HTTP_204_NO_CONTENT)
def deleteQuiz(quiz: Quiz = Depends(check_quiz_owner), db: Session = Depends(get_db)):
    if quiz.isPublished:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Can not delete quiz after publishing")
    db.delete(quiz)
    db.commit()
#**Endpoints for PUBLISHING and USERS TAKING the quiz

#Owner publishing a quiz-- must have at least 1 question, 2 answer options per question, and only one correct answer marked per question
@app.post('/api/quizzes/{quiz_id}/publish', response_model=QuizEditorOut)
def publishQuiz(quiz: Quiz = Depends(check_quiz_owner), db: Session = Depends(get_db)):
    if quiz.isPublished:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Quiz already published.")
    if len(quiz.questions) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Need at least 1 question to publish a quiz.")
    for q in quiz.questions:
        if len(q.answers) < 2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Each question needs at least 2 answer options.")
        numCorrectAnswers=0
        for a in q.answers:
            if a.isCorrect: numCorrectAnswers+=1
        if numCorrectAnswers != 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Each question must have only 1 correct answer.")
    quiz.isPublished = True
    quiz.share_link = secrets.token_urlsafe(8)
    db.commit()
    db.refresh(quiz)
    return quiz
#takable quiz dependency to check the link the user clicked is valid and the quiz is published
def takableQuiz(link:str, db:Session = Depends(get_db)) -> Quiz:
    quiz = db.scalar(select(Quiz).where(Quiz.share_link == link))
    if quiz is None or not quiz.isPublished:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found.")
    return quiz
#route checks that the display name being entered has not been used before to keep them unique for no confusion later on
@app.get('/api/quizzes/take/{link}/check-name')
def checkName(display_name: str, quiz: Quiz = Depends(takableQuiz), db: Session = Depends(get_db)):
    usersWithSameName = db.scalar(select(Attempt).where(Attempt.quiz_id == quiz.id,Attempt.display_name == display_name))
    if usersWithSameName is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Display name already in use, choose a different one.")
    return {"available": True}
#user taking the quiz via the link after clicking start, we are sending the quiz data so frontend can build the quiz up for the user
@app.get('/api/quizzes/{link}/start-quiz', response_model=QuizStartOut)
def startQuiz(quiz: Quiz = Depends(takableQuiz)):
    return quiz
#user submits a quiz to the backend, not calculating score yet just creating in the db
@app.post('/api/quizzes/{link}/submit')
def submitQuiz(body: AttemptSubmitIn, db: Session = Depends(get_db), quiz: Quiz = Depends(takableQuiz)):
    attempt = Attempt(quiz_id=quiz.id, display_name=body.display_name)
    score = 0
    answeredQuestions = set() #one pick per question -- without this a taker could send the same correct answer repeatedly and score higher than the quiz is out of
    for choice in body.picks:
        #check if question id is valid and answer id is from the question we found
        question = next((q for q in quiz.questions if q.id == choice.question_id),None)
        if question is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid question, question id does not exist for the quiz")
        if question.id in answeredQuestions:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only one answer allowed per question.")
        answeredQuestions.add(question.id)
        answer = next((a for a in question.answers if a.id == choice.answer_id),None)
        if answer is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Answer does not exist in the question")
        if answer.isCorrect:
            score += 1
        attempt.answers.append(AnswerAttempt(question_id=choice.question_id, answer_id=choice.answer_id))
    total = len(quiz.questions)
    attempt.score = score
    attempt.percentage_right = round(score / total * 100) if total else 0
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return {"Status": "Submitted"}
#*Endpoint for the dashboard creation, frontend fetches this and uses the data to build the leaderboard
@app.get('/api/quizzes/{quiz_id}/dashboard', response_model=list[DashboardOut])
def getDashboard(quiz: Quiz = Depends(check_quiz_owner), db:Session = Depends(get_db)):
    attempts = db.scalars(select(Attempt).where(Attempt.quiz_id == quiz.id).order_by(Attempt.score.desc()))
    total = len(quiz.questions)
    result = [DashboardOut(score=a.score, display_name=a.display_name, total=total) for a in attempts]
    return result




