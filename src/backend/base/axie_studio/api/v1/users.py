from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.sql.expression import SelectOfScalar

from axie_studio.api.utils import CurrentActiveUser, DbSession
from axie_studio.api.v1.schemas import UsersResponse
from axie_studio.initial_setup.setup import get_or_create_default_folder
from axie_studio.services.auth.utils import (
    get_current_active_superuser,
    get_password_hash,
    verify_password,
)
from axie_studio.services.database.models.user.crud import get_user_by_id, update_user
from axie_studio.services.database.models.user.model import User, UserCreate, UserRead, UserUpdate
from axie_studio.services.deps import get_settings_service
from axie_studio.services.auth.utils import get_current_active_user, get_password_hash

router = APIRouter(tags=["Users"], prefix="/users")


@router.post("/", response_model=UserRead, status_code=201)
async def add_user(
    user: UserCreate,
    session: DbSession,
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Add a new user to the database. Only admins can create users."""
    # Check if current user is admin/superuser
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can create new users."
        )

    new_user = User.model_validate(user, from_attributes=True)
    try:
        new_user.password = get_password_hash(user.password)
        new_user.is_active = get_settings_service().auth_settings.NEW_USER_IS_ACTIVE
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        # Create default folder for the new user
        from axie_studio.services.database.models.folder.crud import get_or_create_default_folder
        folder = await get_or_create_default_folder(session, new_user.id)
        if not folder:
            raise HTTPException(status_code=500, detail="Error creating default project")

    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail="This username is unavailable.") from e

    return new_user


@router.get("/whoami", response_model=UserRead)
async def read_current_user(
    current_user: CurrentActiveUser,
) -> User:
    """Retrieve the current user's data."""
    return current_user


@router.get("/", dependencies=[Depends(get_current_active_superuser)])
async def read_all_users(
    *,
    skip: int = 0,
    limit: int = 10,
    session: DbSession,
) -> UsersResponse:
    """Retrieve a list of users from the database with pagination."""
    query: SelectOfScalar = select(User).offset(skip).limit(limit)
    users = (await session.exec(query)).fetchall()

    count_query = select(func.count()).select_from(User)
    total_count = (await session.exec(count_query)).first()

    return UsersResponse(
        total_count=total_count,
        users=[UserRead(**user.model_dump()) for user in users],
    )


@router.patch("/{user_id}", response_model=UserRead)
async def patch_user(
    user_id: UUID,
    user_update: UserUpdate,
    user: CurrentActiveUser,
    session: DbSession,
) -> User:
    """Update an existing user's data."""
    update_password = bool(user_update.password)

    if not user.is_superuser and user_update.is_superuser:
        raise HTTPException(status_code=403, detail="Permission denied")

    if not user.is_superuser and user.id != user_id:
        raise HTTPException(status_code=403, detail="Permission denied")
    if update_password:
        if not user.is_superuser:
            raise HTTPException(status_code=400, detail="You can't change your password here")
        user_update.password = get_password_hash(user_update.password)

    if user_db := await get_user_by_id(session, user_id):
        if not update_password:
            user_update.password = user_db.password
        return await update_user(user_db, user_update, session)
    raise HTTPException(status_code=404, detail="User not found")


@router.patch("/{user_id}/reset-password", response_model=UserRead)
async def reset_password(
    user_id: UUID,
    user_update: UserUpdate,
    user: CurrentActiveUser,
    session: DbSession,
) -> User:
    """Reset a user's password."""
    if user_id != user.id:
        raise HTTPException(status_code=400, detail="You can't change another user's password")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if verify_password(user_update.password, user.password):
        raise HTTPException(status_code=400, detail="You can't use your current password")
    new_password = get_password_hash(user_update.password)
    user.password = new_password
    await session.commit()
    await session.refresh(user)

    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_superuser)],
    session: DbSession,
) -> dict:
    """Delete a user from the database."""
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="You can't delete your own user account")
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Permission denied")

    stmt = select(User).where(User.id == user_id)
    user_db = (await session.exec(stmt)).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    await session.delete(user_db)
    await session.commit()

    return {"detail": "User deleted"}
