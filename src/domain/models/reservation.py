class Reservation:
    def __init__(self, id, user_id, provider_id, space_id=None, package_id=None,
                 start_time=None, end_time=None, total_price=0, status='pending',
                 qr_code=None, created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.provider_id = provider_id
        self.space_id = space_id
        self.package_id = package_id
        self.start_time = start_time
        self.end_time = end_time
        self.total_price = total_price
        self.status = status
        self.qr_code = qr_code
        self.created_at = created_at
        self.updated_at = updated_at


class ReservationItem:
    def __init__(self, id, reservation_id, item_type, item_id, quantity=1,
                 price_at_booking=0):
        self.id = id
        self.reservation_id = reservation_id
        self.item_type = item_type
        self.item_id = item_id
        self.quantity = quantity
        self.price_at_booking = price_at_booking


class Payment:
    def __init__(self, id, reservation_id, user_id, amount, method='cash',
                 status='pending', transaction_ref=None, created_at=None):
        self.id = id
        self.reservation_id = reservation_id
        self.user_id = user_id
        self.amount = amount
        self.method = method
        self.status = status
        self.transaction_ref = transaction_ref
        self.created_at = created_at


class ServiceSession:
    def __init__(self, id, reservation_id, checked_in_at=None, checked_out_at=None,
                 actual_duration_minutes=None, status='in_progress'):
        self.id = id
        self.reservation_id = reservation_id
        self.checked_in_at = checked_in_at
        self.checked_out_at = checked_out_at
        self.actual_duration_minutes = actual_duration_minutes
        self.status = status


class Review:
    def __init__(self, id, reservation_id, user_id, space_id=None, rating=5,
                 comment=None, created_at=None):
        self.id = id
        self.reservation_id = reservation_id
        self.user_id = user_id
        self.space_id = space_id
        self.rating = rating
        self.comment = comment
        self.created_at = created_at
