import random
import shutil
import string
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from sqlalchemy.orm import Session
from auth.outh2 import get_current_user
from database.database import get_db
from routers.schemas import PostBase, PostDisplay, UserAuth
from database import db_post


router = APIRouter(prefix="/post", tags=["Post"])


@router.post("", response_model=PostDisplay)
async def create_post(post: PostBase, db: Session = Depends(get_db), current_user:UserAuth = Depends(get_current_user)):
    """Creates a post and saves to the database only for logged users.

    Args:
        post (PostBase): the post
        db (Session, optional): the database. Defaults to Depends(get_db).
        current_user (UserAuth, optional): logged user. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: image path not correct

    Returns:
        dict: the post
    """
    image_url_types = ["absolute", "relative"]
    
    if not post.image_url_type in image_url_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="image url type must be of type absolute or relative.",
        )

    return db_post.create_post(post, db, current_user.id)


@router.get('', response_model=list[PostDisplay])
async def get_posts(db:Session = Depends(get_db)):
    """Get all posted posts

    Args:
        db (Session, optional): the database. Defaults to Depends(get_db).

    Returns:
        list: all posts
    """
    return db_post.retrive_posts(db)

@router.delete('/{id}')
async def delete_post(id: int, db:Session = Depends(get_db), current_user:UserAuth = Depends(get_current_user)):
    """Delete a post only of you are the creater or the admin.

    Args:
        id (int): post id
        db (Session, optional): the database. Defaults to Depends(get_db).
        current_user (UserAuth, optional): logged user. Defaults to Depends(get_current_user).

    Returns:
        None: 200 ok if deleted
    """
    return db_post.delete_post(id, db, current_user.id)


@router.post('/image')
async def upload_image(image: UploadFile = File(...), current_user:UserAuth = Depends(get_current_user)):
    """Uploads an image to the server

    Args:
        image (UploadFile, optional): the image file. Defaults to File(...).
        current_user (UserAuth, optional): logged user. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: image file not supporteed

    Returns:
        str: file name saved in server
    """
    rand_str = ''.join(random.choice(string.ascii_letters) for i in range(10))

    image_file_type = image.filename.rsplit('.', 1)[1]
    allowed_image_types = {"jpg", "png", "jpeg", "webm", "gif"}

    if image_file_type not in allowed_image_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= f'Image format not supported, supported formarts are {", ".join(allowed_image_types)}.')
    
    filename = f'_{rand_str}.'.join(image.filename.rsplit('.', 1))

    path = f'images/{filename}'

    with open(path, 'w+b') as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    return {'filename': path}
