from fastapi import FastAPI, Request, Depends, HTTPException, status
from database import Base, engine, get_db
from config import settings
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from schemas import RegisterIn, LoginIn, UserOut
from models import User
import bcrypt

Base.metadata.create_all(bind=engine) #create the tables on startup

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret) #the session middleware to check the sessions using the secret comparing to signature passed thorugh the header

#sign up route
@app.post('/api/auth/signup', response_model=UserOut)
def signUp(registerInfo: RegisterIn, db: Session = Depends(get_db)):
    userCheck = db.scalar(select(User).where(registerInfo.display_name == User.display_name))
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
