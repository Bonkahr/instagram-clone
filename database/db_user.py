from sqlalchemy.orm.session import Session
from fastapi import HTTPException, status

from database.hashing import Hash
from routers.schemas import UserBase
from .models import DbUser


def create_user(request: UserBase, db: Session):
    """Saves a user to the databse if all the requirements are met

    Args:
        request (UserBase): User details 
        db (): the database

    Raises:
        HTTPException: Username less than 3 chars
        HTTPException: password less than 6 chars
        HTTPException: password similar to username
        HTTPException: user type not correct
        HTTPException: user already in the database

    Returns:
        dict : User details
    """
    if len(request.username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"username must be more than 3 characters.",
        )

    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User password must be atleast 6 characters.",
        )

    if request.password.startswith(request.username[0:3]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User password must not start-with username characters.",
        )
    
    user_types = ['admin', 'user']
    if request.user_type is not None:
        if request.user_type.lower() not in user_types:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'User type must be either admin or user.') 
    
        user_type = request.user_type.lower()
    else:
        user_type = 'user'

    new_user = DbUser(
        username=request.username.lower(),
        email=request.email.lower(),
        user_type=user_type,
        password=Hash.bcrypt(request.password),
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with username {request.username} or email {request.email} already exists.",
        )


def all_users(db: Session, user_id: int):
    """Get a list of all users only if you are an admin

    Args:
        db (Session): the database
        user_id (int): the current logged user

    Raises:
        HTTPException: current user not admin

    Returns:
        dict: all users
    """
    current_user = db.query(DbUser).filter(DbUser.id == user_id).first()

    if current_user.user_type != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'You are not authorized to this information.')

    return db.query(DbUser).all()


def delete_user(id: int, db: Session, user_id: int):
    """Delete a user using his id if you are an admin

    Args:
        id (int): id of user to delete
        db (Session): the database
        user_id (int): the current logged user

    Raises:
        HTTPException: logged user not admin

    Returns:
        None: 200 ok if success.
    """
    current_user = db.query(DbUser).filter(DbUser.id == user_id).first()

    if current_user.user_type != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'You have no authority to delete any user.')

    user = db.query(DbUser).filter(DbUser.id == id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT, detail=f"No user with id {id}"
        )

    if user.user_type == 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not allowed to delete an admin.')

    db.delete(user)
    db.commit()


def get_user_by_username(username:str ,db:Session):
    """Get a user form the database using the username

    Args:
        username (str): user username
        db (Session): the database

    Raises:
        HTTPException: no user found

    Returns:
        dict: user details
    """
    user = db.query(DbUser).filter(DbUser.username == username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No user with username: {username} registered.')

    return user
