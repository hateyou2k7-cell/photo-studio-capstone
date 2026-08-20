class SpaceSchedule:
    def __init__(self, id: int, space_id: int, day_of_week: int, start_time, end_time,
                 is_available: bool, created_at, updated_at):
        self.id = id
        self.space_id = space_id
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time
        self.is_available = is_available
        self.created_at = created_at
        self.updated_at = updated_at