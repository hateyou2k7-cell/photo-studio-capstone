from typing import List, Optional
from business.models.post import Post, Comment
from business.models.workshop import Workshop, WorkshopRegistration
from business.models.ipost_repository import IPostRepository
from business.models.iworkshop_repository import IWorkshopRepository

POST_CATEGORIES = {'article', 'tutorial', 'equipment_review', 'technique'}
WORKSHOP_STATUSES = {'open', 'full', 'cancelled', 'done'}


class CommunityService:
    def __init__(self, post_repo: IPostRepository, workshop_repo: IWorkshopRepository):
        self.post_repo = post_repo
        self.workshop_repo = workshop_repo

    # --- Posts ---

    def create_post(self, author_id: int, title: str, content: str,
                    category='article', is_published=True) -> Post:
        if not title or not title.strip():
            raise ValueError('title is required')
        if not content or not content.strip():
            raise ValueError('content is required')
        if category not in POST_CATEGORIES:
            raise ValueError(f'category must be one of {POST_CATEGORIES}')
        post = Post(
            id=None, author_id=author_id, title=title.strip(),
            content=content.strip(), category=category,
            is_published=is_published,
        )
        return self.post_repo.add(post)

    def get_post(self, post_id: int) -> Optional[Post]:
        post = self.post_repo.get_by_id(post_id)
        if post:
            self.post_repo.increment_view(post_id)
        return post

    def list_posts(self, author_id=None, category=None) -> List[Post]:
        return self.post_repo.list(author_id=author_id, category=category)

    def update_post(self, post_id: int, title: str, content: str,
                    category='article', is_published=True) -> Post:
        existing = self.post_repo.get_by_id(post_id)
        if not existing:
            raise ValueError('Post not found')
        if category not in POST_CATEGORIES:
            raise ValueError(f'category must be one of {POST_CATEGORIES}')
        post = Post(
            id=post_id, author_id=existing.author_id, title=title.strip(),
            content=content.strip(), category=category,
            is_published=is_published,
        )
        return self.post_repo.update(post)

    def delete_post(self, post_id: int) -> None:
        existing = self.post_repo.get_by_id(post_id)
        if not existing:
            raise ValueError('Post not found')
        self.post_repo.delete(post_id)

    # --- Comments ---

    def add_comment(self, post_id: int, user_id: int, content: str) -> Comment:
        post = self.post_repo.get_by_id(post_id)
        if not post:
            raise ValueError('Post not found')
        if not content or not content.strip():
            raise ValueError('content is required')
        comment = Comment(
            id=None, post_id=post_id, user_id=user_id,
            content=content.strip(),
        )
        return self.post_repo.add_comment(comment)

    def list_comments(self, post_id: int) -> List[Comment]:
        post = self.post_repo.get_by_id(post_id)
        if not post:
            raise ValueError('Post not found')
        return self.post_repo.list_comments(post_id)

    def delete_comment(self, comment_id: int) -> None:
        self.post_repo.delete_comment(comment_id)

    # --- Workshops ---

    def create_workshop(self, expert_id: int, title: str, scheduled_at,
                        description=None, location=None, capacity=10,
                        price=0) -> Workshop:
        if not title or not title.strip():
            raise ValueError('title is required')
        if not scheduled_at:
            raise ValueError('scheduled_at is required')
        if capacity < 1:
            raise ValueError('capacity must be at least 1')
        workshop = Workshop(
            id=None, expert_id=expert_id, title=title.strip(),
            description=description, scheduled_at=scheduled_at,
            location=location, capacity=capacity, price=price,
        )
        return self.workshop_repo.add(workshop)

    def get_workshop(self, workshop_id: int) -> Optional[Workshop]:
        return self.workshop_repo.get_by_id(workshop_id)

    def list_workshops(self, expert_id=None, status=None) -> List[Workshop]:
        return self.workshop_repo.list(expert_id=expert_id, status=status)

    def update_workshop(self, workshop_id: int, title: str, scheduled_at,
                        description=None, location=None, capacity=10,
                        price=0, status='open') -> Workshop:
        existing = self.workshop_repo.get_by_id(workshop_id)
        if not existing:
            raise ValueError('Workshop not found')
        if status not in WORKSHOP_STATUSES:
            raise ValueError(f'status must be one of {WORKSHOP_STATUSES}')
        workshop = Workshop(
            id=workshop_id, expert_id=existing.expert_id, title=title.strip(),
            description=description, scheduled_at=scheduled_at,
            location=location, capacity=capacity, price=price, status=status,
        )
        return self.workshop_repo.update(workshop)

    def delete_workshop(self, workshop_id: int) -> None:
        existing = self.workshop_repo.get_by_id(workshop_id)
        if not existing:
            raise ValueError('Workshop not found')
        self.workshop_repo.delete(workshop_id)

    # --- Workshop Registration ---

    def register_workshop(self, workshop_id: int, user_id: int) -> WorkshopRegistration:
        workshop = self.workshop_repo.get_by_id(workshop_id)
        if not workshop:
            raise ValueError('Workshop not found')
        if workshop.status != 'open':
            raise ValueError('Workshop is not open for registration')
        count = self.workshop_repo.count_registrations(workshop_id)
        if count >= workshop.capacity:
            self.workshop_repo.update(Workshop(
                id=workshop.id, expert_id=workshop.expert_id, title=workshop.title,
                description=workshop.description, scheduled_at=workshop.scheduled_at,
                location=workshop.location, capacity=workshop.capacity,
                price=workshop.price, status='full',
            ))
            raise ValueError('Workshop is full')
        reg = WorkshopRegistration(
            id=None, workshop_id=workshop_id, user_id=user_id,
        )
        return self.workshop_repo.register(reg)

    def list_registrations(self, workshop_id: int) -> List[WorkshopRegistration]:
        workshop = self.workshop_repo.get_by_id(workshop_id)
        if not workshop:
            raise ValueError('Workshop not found')
        return self.workshop_repo.list_registrations(workshop_id)

    def cancel_registration(self, registration_id: int) -> WorkshopRegistration:
        return self.workshop_repo.cancel_registration(registration_id)
