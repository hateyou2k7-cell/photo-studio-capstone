class Room:
    def __init__(self, id: int, name: str, description: str, room_type: str,
                 capacity: int, price_per_hour: float, status: str, created_at, updated_at):
        self.id = id
        self.name = name
        self.description = description
        self.room_type = room_type
        self.capacity = capacity
        self.price_per_hour = price_per_hour
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at