from fastapi import APIRouter, Depends

from database.database import get_db
from .schemas import UserAuth
from auth.outh2 import get_current_user
from database import comment


from sqlalchemy.orm import Session

from .schemas import CommentBase, CommentDisplay


router = APIRouter(
    prefix='/comment',
    tags=['Comment']
)


@router.post('/{post_id}', response_model=CommentBase)
async def create_comment(request: CommentBase, post_id, db:Session = Depends(get_db), current_user:UserAuth = Depends(get_current_user)):
    return comment.create_comment(request, current_user.id, post_id, db)


@router.get('/{post_id}', response_model=list[CommentDisplay])
async def all_comments(post_id: int, db: Session = Depends(get_db)):
    return comment.get_all_comments(db, post_id)


@router.delete('/{comment_id}')
async def delete_comment(comment_id: int, db:Session = Depends(get_db), current_user:UserAuth = Depends(get_current_user)):
    return comment.delete_comment(comment_id, db, current_user.id)