from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from routers.schemas import UserBase, UserDisplay
from database import db_user
from database.database import get_db
from .schemas import UserAuth

from auth.outh2 import get_current_user

router = APIRouter(prefix="/user", tags=["User"])


@router.post("", response_model=UserDisplay)
async def create_user(request: UserBase, db: Session = Depends(get_db)):
    """Creates a new user

    Args:
        request (UserBase): the user details
        db (Session, optional): the database. Defaults to Depends(get_db).

    Returns:
        dict: user details
    """
    return db_user.create_user(request, db)


@router.get('', response_model=list[UserDisplay])
async def get_all_users(db:Session = Depends(get_db), current_user:UserAuth = Depends(get_current_user)):
    """Get a list of all registered user if you are an admin

    Args:
        db (Session, optional): the database. Defaults to Depends(get_db).
        current_user (UserAuth, optional): logged user. Defaults to Depends(get_current_user).

    Returns:
        list: all users
    """
    return db_user.all_users(db, current_user.id)


@router.delete('/{id}')
async def delete_user(id: int, db: Session = Depends(get_db), current_user:UserAuth = Depends(get_current_user)):
    """Delete a user only if you are the admin

    Args:
        id (int): user is
        db (Session, optional): the database. Defaults to Depends(get_db).
        current_user (UserAuth, optional): logged user. Defaults to Depends(get_current_user).

    Returns:
        None: 200 OK if user deleted
    """
    return db_user.delete_user(id, db, current_user.id)
