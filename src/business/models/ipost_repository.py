from abc import ABC, abstractmethod
from typing import List, Optional
from .post import Post, Comment


class IPostRepository(ABC):
    @abstractmethod
    def add(self, post: Post) -> Post:
        pass

    @abstractmethod
    def get_by_id(self, post_id: int) -> Optional[Post]:
        pass

    @abstractmethod
    def list(self, author_id=None, category=None, published_only=True) -> List[Post]:
        pass

    @abstractmethod
    def update(self, post: Post) -> Post:
        pass

    @abstractmethod
    def delete(self, post_id: int) -> None:
        pass

    @abstractmethod
    def increment_view(self, post_id: int) -> None:
        pass

    @abstractmethod
    def add_comment(self, comment: Comment) -> Comment:
        pass

    @abstractmethod
    def list_comments(self, post_id: int) -> List[Comment]:
        pass

    @abstractmethod
    def delete_comment(self, comment_id: int) -> None:
        pass
