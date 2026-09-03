class Workshop:
    def __init__(self, id, expert_id, title, description=None, scheduled_at=None,
                 location=None, capacity=10, price=0, status='open'):
        self.id = id
        self.expert_id = expert_id
        self.title = title
        self.description = description
        self.scheduled_at = scheduled_at
        self.location = location
        self.capacity = capacity
        self.price = price
        self.status = status


class WorkshopRegistration:
    def __init__(self, id, workshop_id, user_id, status='registered', registered_at=None):
        self.id = id
        self.workshop_id = workshop_id
        self.user_id = user_id
        self.status = status
        self.registered_at = registered_at
