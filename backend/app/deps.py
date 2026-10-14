"""Reusable FastAPI dependencies.

Dependencies replace Rails' before_action filters. An endpoint declares what it
needs as a parameter, e.g. `user: CurrentUser`, and FastAPI runs the function
that provides it before the endpoint (raising 401/404 stops the request early).
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Baby, Caregiving, User
from app.security import decode_access_token

# Tells FastAPI (and the /docs "Authorize" button) where tokens come from.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# `Annotated` bundles a type with its dependency so endpoints can just write
# `db: DbSession` instead of `db: Session = Depends(get_db)` every time.
DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(db: DbSession, token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    user_id = decode_access_token(token)
    user = db.get(User, user_id) if user_id is not None else None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_baby_for_user(baby_id: int, db: DbSession, user: CurrentUser) -> Baby:
    """Load a baby the current user is an accepted caregiver of.

    Returns 404 (not 403) for babies you can't access, so the API doesn't
    reveal which ids exist. Any route with `{baby_id}` in its path can use this.
    """
    baby = db.scalar(
        select(Baby)
        .join(Caregiving)
        .where(
            Baby.id == baby_id,
            Caregiving.user_id == user.id,
            Caregiving.accepted_at.is_not(None),
        )
    )
    if baby is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Baby not found")
    return baby


AccessibleBaby = Annotated[Baby, Depends(get_baby_for_user)]
