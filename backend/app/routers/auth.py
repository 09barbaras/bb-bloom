"""Sign up, log in, and "who am I".

A router is roughly a Rails controller plus its routes.rb entries in one file.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.deps import CurrentUser, DbSession
from app.models import User
from app.schemas.auth import SignupRequest, Token, UserRead
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(body: SignupRequest, db: DbSession) -> Token:
    email = body.email.lower()
    if db.scalar(select(User).where(User.email == email)) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email is already registered")

    user = User(email=email, name=body.name, password_digest=hash_password(body.password))
    db.add(user)
    db.commit()  # unlike ActiveRecord's save, nothing hits the DB until commit
    return Token(access_token=create_access_token(user.id))


@router.post("/token", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession) -> Token:
    """Log in with a form-encoded `username` (the email) and `password`.

    This is the standard OAuth2 password flow, which is why the field is called
    `username`. It's also what makes the "Authorize" button on /docs work.
    """
    user = db.scalar(select(User).where(User.email == form.username.lower()))
    if user is None or not verify_password(form.password, user.password_digest):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser) -> User:
    return user
