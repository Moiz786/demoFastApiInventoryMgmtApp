from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt

import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import hmac as crypto_hmac
from pydantic import ValidationError
from starlette import status

from models import AuthUser, TokenPayload, UserTable

from db_init import SessionLocal

ACCESS_TOKEN_EXPIRE_MINUTES = 10  # minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 2  # 2 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = "17b5e0c2a36a0a92c1731b8c1c66edfe0d9be509a079f8d7e510e2cfae06eb87"  # should be kept secret
JWT_REFRESH_SECRET_KEY = "d57db9140fcdcffa2e71f93d49d0a19216b52c5702c93e98df064d937f83332d"  # should be kept secret
context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    """
    This function takes a password as input and returns its hashed representation as a string.
    Parameters: password (str): The password to be hashed.
    Returns: encoded_signature (str): The hashed representation of the password, encoded as a URL-safe base64 string with padding characters removed.
    """
    hmac_key = crypto_hmac.HMAC(JWT_SECRET_KEY.encode('utf-8'), hashes.SHA256())
    hmac_key.update(password.encode("utf-8"))
    signature = hmac_key.finalize()

    encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("utf-8")

    return encoded_signature


def confirm(password: str, hashed_pass: str) -> bool:
    """
    Endpoint to verify password
    :param password: input password to match
    :param hashed_pass: stored password in hashed form
    :return: True or False
    """
    return context.verify(password, hashed_pass)


def create_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    """
    Endpont to create token
    :param subject (Union[str, Any]): The subject to be encoded in the token. This can be a string or any other value.
    :param expires_delta (int, optional): The expiration time of the token in seconds. If not provided, the token will expire
     after the time specified in the ACCESS_TOKEN_EXPIRE_MINUTES constant.
    :return: encode string
    """
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    """
        Endpoint to refresh toekn
        :param subject (Union[str, Any]): The subject to be encoded in the token. This can be a string or any other value.
        :param expires_delta (int, optional): The expiration time of the token in seconds. If not provided, the token will expire
         after the time specified in the ACCESS_TOKEN_EXPIRE_MINUTES constant.
        :return: encode string
        """
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt


reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="JWT"
)


async def get_current_user(token: str = Depends(reuseable_oauth)) -> AuthUser:
    """
        Endpoint to get current user
        :param token: string value of token
        :return: AuthUser model data
        """
    try:
        from db_init import SessionLocal
        db = SessionLocal()
        payload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )
        user = db.query(UserTable).filter(UserTable.email == payload['sub']).first()
        payload['username'] = user.name
        token_data = TokenPayload(**payload)

        # if token_data.exp.strftime('%s') < datetime.now().strftime('%s'):
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Token expired",
        #         headers={"WWW-Authenticate": "Bearer"},
        #     )
    except(jwt.JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db = SessionLocal()
    # user: Union[dict[str, Any], None] = db.get(token_data.sub, None)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return AuthUser(name=user.name, email=user.email)
