import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from . import models
from routers.schemas import CommentBase

def create_comment(request: CommentBase, user_id: int, post_id: int, db: Session):
    user = db.query(models.DbUser).filter(models.DbUser.id == user_id).first()
    new_comment = models.DbComment(
        comment = request.comment,
        username = user.username,
        timestamp = datetime.datetime.now(),
        post_id = post_id,
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    return new_comment


def get_all_comments(db: Session, post_id: int):
    return db.query(models.DbComment).filter(models.DbComment.post_id == post_id).al()



def delete_comment(comment_id: int, db: Session, user_id: int):
    comment = db.query(models.DbComment).filter(models.DbComment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No comment with id {comment_id}.')
    
    user = db.query(models.DbUser).filter(models.DbUser.id == user_id).first()
    post = db.query(models.DbPost).filter(models.DbPost.id == comment.post_id).first()
    post_owner = db.query(models.DbUser).filter(models.DbUser.id == post.user_id).first()
    

    if user.username == comment.username or user.user_type == 'admin' or post_owner.username == user.username:
        db.delete(comment)
        db.commit()
        
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='You are not authorized to delete this comment, contact the admin, the post owner or the comment owner.')

    
    
