class SpaceImage:
    def __init__(self, id: int, space_id: int, url: str, is_primary: bool, sort_order: int, created_at):
        self.id = id
        self.space_id = space_id
        self.url = url
        self.is_primary = is_primary
        self.sort_order = sort_order
        self.created_at = created_at