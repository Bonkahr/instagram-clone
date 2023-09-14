import datetime
from fastapi import HTTPException, status

from sqlalchemy.orm.session import Session

from routers.schemas import PostBase
from . import models


def create_post(request: PostBase, db: Session, user_id: int):
    """Create a post only if you a logged in.

    Args:
        request (PostBase): the post details
        db (Session): the database
        user_id (int): logged in user id

    Raises:
        HTTPException: image url type not correct
        HTTPException: image format not supported

    Returns:
        dict: post details
    """
    if request.image_url.startswith("https://"):
        media_type = "absolute"
    else:
        media_type = "relative"

    if request.image_url_type != media_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kindly verify image_url_type.",
        )

    allowed_image_formats = {"jpg", "png", "jpeg", "webm", "gif"}
    media_format = request.image_url.rsplit(".", 1)[1]


    if media_type == 'relative' and media_format.lower() not in allowed_image_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The format '{media_format}' is not supported",
        )

    new_post = models.DbPost(
        image_url=request.image_url,
        image_url_type=media_type,
        caption=request.caption,
        timestamp=datetime.datetime.now(),
        user_id=user_id,
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


def retrive_posts(db: Session):
    """Retrieve all the posts i the database

    Args:
        db (Session): the database

    Returns:
        list: posts
    """
    return db.query(models.DbPost).all()


def delete_post(id: int, db: Session, user_id: int):
    """Delete a post only if you are the one created it or you are an admin.

    Args:
        id (int): post id
        db (Session): the database
        user_id (int): logged user is

    Raises:
        HTTPException: no such post in database
        HTTPException: you are not the creater of the post or the admin.
    """
    post = db.query(models.DbPost).filter(models.DbPost.id == id).first()
    user = db.query(models.DbUser).filter(models.DbUser.id == user_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No post with id {id}."
        )
    
    post_owner = db.query(models.DbUser).filter(models.DbUser.username == post.user.username).first()

    if post_owner.id == user_id or user.user_type == 'admin':
        db.delete(post)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'You can only delete the post you create.')
    
    
