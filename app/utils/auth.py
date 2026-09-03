from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.config import get_db
from app.database import models
from app.utils.tokens import TokenUtils

# extract token from authorization header
# "tokenUrl" MUST match our auth route
# allows for authorization button in docs, making API testing MUCH easier
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> models.User:

    user_id = TokenUtils.verify_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Oh no! You are not authorized to perform this action. Try again?",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(user_id)
    except TypeError, ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Oh no! you are not authorized to peform this action. Try again?",
            headers={"WWW-Authenticate": "Bearer"},
        )

    data = await db.execute(select(models.User).where(models.User.id == user_id))
    existing_user = data.scalars().first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Oops! User does not exist. Try again?",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return existing_user
