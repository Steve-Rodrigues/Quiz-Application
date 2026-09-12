##*********Authentication section(registerIn, loginIn, userOut) request/response data
from pydantic import BaseModel, EmailStr, ConfigDict

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

