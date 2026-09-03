class Post:
    def __init__(self, id, author_id, title, content, category='article',
                 is_published=True, view_count=0, created_at=None, updated_at=None):
        self.id = id
        self.author_id = author_id
        self.title = title
        self.content = content
        self.category = category
        self.is_published = is_published
        self.view_count = view_count
        self.created_at = created_at
        self.updated_at = updated_at


class Comment:
    def __init__(self, id, post_id, user_id, content, created_at=None):
        self.id = id
        self.post_id = post_id
        self.user_id = user_id
        self.content = content
        self.created_at = created_at
