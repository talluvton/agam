from typing import Annotated
from fastapi import APIRouter, Depends
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm
from schemas.user import User, Token
from clients.auth import AuthClient

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    return AuthClient.create_user(user)


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return AuthClient.login_for_access_token(form_data)
