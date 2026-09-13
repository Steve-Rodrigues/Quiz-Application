from fastapi import FastAPI, Request, Depends, HTTPException, status
from database import Base, engine, get_db
from config import settings
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from schemas import RegisterIn, LoginIn, UserOut,QuizCreateIn, QuizEditorOut
from models import User, Quiz, Question, Answer
import bcrypt

Base.metadata.create_all(bind=engine) #create the tables on startup

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret) #the session middleware to check the sessions using the secret comparing to signature passed thorugh the header

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
    if quiz.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not the owner of this quiz.")
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No quizzes for this user.")
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

    



