from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from business.models.ipost_repository import IPostRepository
from business.models.post import Post, Comment
from database.models.film_community_model import Post as PostModel, Comment as CommentModel
from database.databases.factory_database import FactoryDatabase as db_factory


class PostRepository(IPostRepository):
    def __init__(self, session: Session = None):
        self.session = session or db_factory.get_database('POSTGREE').session

    def add(self, post: Post) -> PostModel:
        try:
            model = PostModel(
                author_id=post.author_id,
                title=post.title,
                content=post.content,
                category=post.category,
                is_published=post.is_published,
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except Exception as e:
            self.session.rollback()
            raise ValueError('Could not create post')

    def get_by_id(self, post_id: int) -> Optional[PostModel]:
        return self.session.query(PostModel).filter_by(id=post_id).first()

    def list(self, author_id=None, category=None, published_only=True) -> List[PostModel]:
        query = self.session.query(PostModel)
        if published_only:
            query = query.filter_by(is_published=True)
        if author_id is not None:
            query = query.filter_by(author_id=author_id)
        if category is not None:
            query = query.filter_by(category=category)
        return query.order_by(PostModel.created_at.desc()).all()

    def update(self, post: Post) -> PostModel:
        try:
            existing = self.session.query(PostModel).filter_by(id=post.id).first()
            if not existing:
                raise ValueError('Post not found')
            existing.title = post.title
            existing.content = post.content
            existing.category = post.category
            existing.is_published = post.is_published
            self.session.commit()
            self.session.refresh(existing)
            return existing
        except ValueError:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Could not update post')

    def delete(self, post_id: int) -> None:
        try:
            model = self.session.query(PostModel).filter_by(id=post_id).first()
            if model:
                self.session.delete(model)
                self.session.commit()
            else:
                raise ValueError('Post not found')
        except ValueError:
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Could not delete post')

    def increment_view(self, post_id: int) -> None:
        try:
            existing = self.session.query(PostModel).filter_by(id=post_id).first()
            if existing:
                existing.view_count = (existing.view_count or 0) + 1
                self.session.commit()
        except Exception:
            self.session.rollback()

    def add_comment(self, comment: Comment) -> CommentModel:
        try:
            model = CommentModel(
                post_id=comment.post_id,
                user_id=comment.user_id,
                content=comment.content,
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except Exception:
            self.session.rollback()
            raise ValueError('Could not add comment')

    def list_comments(self, post_id: int) -> List[CommentModel]:
        return self.session.query(CommentModel).filter_by(post_id=post_id).order_by(CommentModel.created_at.asc()).all()

    def delete_comment(self, comment_id: int) -> None:
        try:
            model = self.session.query(CommentModel).filter_by(id=comment_id).first()
            if model:
                self.session.delete(model)
                self.session.commit()
            else:
                raise ValueError('Comment not found')
        except ValueError:
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Could not delete comment')
