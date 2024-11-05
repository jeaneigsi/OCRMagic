

from fastapi import FastAPI, Body,APIRouter

from models.secure.auth_handler import sign_jwt
from models.secure.base_model import UserSchema, UserLoginSchema

users=[]

router = APIRouter()


@router.post("/user/signup")
async def create_user(user: UserSchema = Body(...)):
    users.append(user) # replace with db call, making sure to hash the password first
    return sign_jwt(user.email)


def check_user(data: UserLoginSchema):
    for user in users:
        if user.email == data.email and user.password == data.password:
            return True
    return False

@router.post("/user/login")
async def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user):
        return sign_jwt(user.email)
    return {
        "error": "Wrong login details!"
    }