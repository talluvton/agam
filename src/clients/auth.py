from fastapi import HTTPException, Depends
from datetime import timedelta, datetime, timezone
from database import db
from starlette import status
from schemas.user import User
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_EXPIRATION_MINUTES = int(os.getenv("TOKEN_EXPIRATION_MINUTES"))

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class AuthClient():

    @classmethod
    def authenticate_user(cls, username: str, password: str):
        try:
            with db.conn.cursor() as cursor:
                cursor.callproc("get_user_by_username", (username,))
                user_record = cursor.fetchone()
            if not user_record:
                return False
            if not bcrypt_context.verify(password, user_record[2]):
                return False
            return user_record
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error authenticate user: {str(e)}")

    @classmethod
    def create_access_token(cls, username: str, user_id: int, expires_delta: timedelta):
        encode = {'sub': username, 'id': user_id}
        expires = datetime.now(timezone.utc) + expires_delta
        encode.update({'exp': expires})
        return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    @classmethod
    def get_current_user(cls, token: Annotated[str, Depends(oauth2_bearer)]):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get('sub')
            user_id: int = payload.get('id')
            if username is None or user_id is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
            return {'username': username, 'id': user_id}
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

    @classmethod
    def create_user(cls, user: User):
        try:
            with db.conn.cursor() as cursor:
                hashed_password=bcrypt_context.hash(user.password)
                cursor.callproc("insert_user", (user.username, hashed_password))
                db.commit()  
            return {"user": user.username, "message": "User created successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

       
    @classmethod
    def login_for_access_token(cls, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
        user = cls.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        user_id=user[0]
        username=user[1]
        token = cls.create_access_token(username, user_id, timedelta(minutes=TOKEN_EXPIRATION_MINUTES))

        return {'access_token': token, 'token_type': 'bearer'}