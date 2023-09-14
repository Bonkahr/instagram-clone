from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from sqlalchemy.orm.session import Session
from auth.outh2 import create_access_token

from database.database import get_db
from database.models import DbUser
from database.hashing import Hash


router = APIRouter(
    tags=['Authentication']
)

@router.post('/login')
async def login(request: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    """_Nothing for you here. Handles logins and logouts_
    """
    request_username = request.username.lower()
    user = db.query(DbUser).filter(DbUser.username == request_username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invalid username.')
    
    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Incorrect password.')
    access_token = create_access_token(data={'username': user.username})

    return {
        'access_token': access_token,
        'token_type': 'bearer',
        'user_id': user.id,
        'username': user.username,
        'user_type': user.user_type,
    }

