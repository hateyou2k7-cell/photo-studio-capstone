import pytest
from datetime import datetime, timedelta
from services.reservation_service import ReservationService, RESERVATION_STATUSES


class FakeReservationRepo:
    def __init__(self):
        self.reservations = []
        self.items = []
        self.payments = []
        self.sessions = []
        self.reviews = []
        self._id_counter = 1
        self._item_counter = 1
        self._payment_counter = 1
        self._session_counter = 1
        self._review_counter = 1

    def add(self, reservation):
        reservation.id = self._id_counter
        self._id_counter += 1
        self.reservations.append(reservation)
        return reservation

    def get_by_id(self, reservation_id):
        return next((r for r in self.reservations if r.id == reservation_id), None)

    def list(self, user_id=None, provider_id=None, status=None):
        result = self.reservations
        if user_id is not None:
            result = [r for r in result if r.user_id == user_id]
        if provider_id is not None:
            result = [r for r in result if r.provider_id == provider_id]
        if status is not None:
            result = [r for r in result if r.status == status]
        return result

    def update(self, reservation):
        for i, r in enumerate(self.reservations):
            if r.id == reservation.id:
                self.reservations[i] = reservation
                return reservation
        raise ValueError('Reservation not found')

    def delete(self, reservation_id):
        self.reservations = [r for r in self.reservations if r.id != reservation_id]

    def update_status(self, reservation_id, status):
        r = self.get_by_id(reservation_id)
        if r:
            r.status = status
            return r
        raise ValueError('Reservation not found')

    def add_item(self, item):
        item.id = self._item_counter
        self._item_counter += 1
        self.items.append(item)
        return item

    def list_items(self, reservation_id):
        return [i for i in self.items if i.reservation_id == reservation_id]

    def add_payment(self, payment):
        payment.id = self._payment_counter
        self._payment_counter += 1
        self.payments.append(payment)
        return payment

    def get_payment(self, reservation_id):
        return next((p for p in self.payments if p.reservation_id == reservation_id), None)

    def update_payment_status(self, payment_id, status):
        p = next((p for p in self.payments if p.id == payment_id), None)
        if p:
            p.status = status
            return p
        raise ValueError('Payment not found')

    def create_session(self, session):
        session.id = self._session_counter
        self._session_counter += 1
        self.sessions.append(session)
        return session

    def check_in(self, reservation_id):
        from business.models.reservation import ServiceSession
        session = ServiceSession(
            id=self._session_counter, reservation_id=reservation_id,
            checked_in_at=datetime.utcnow(), status='in_progress',
        )
        self._session_counter += 1
        self.sessions.append(session)
        return session

    def check_out(self, reservation_id):
        session = next((s for s in self.sessions if s.reservation_id == reservation_id), None)
        if session:
            session.checked_out_at = datetime.utcnow()
            session.actual_duration_minutes = 30
            session.status = 'completed'
            return session
        raise ValueError('No active session')

    def add_review(self, review):
        review.id = self._review_counter
        self._review_counter += 1
        self.reviews.append(review)
        return review

    def list_reviews(self, space_id):
        return [r for r in self.reviews if r.space_id == space_id]

    def check_overlap(self, space_id, start_time, end_time, exclude_id=None):
        for r in self.reservations:
            if r.space_id == space_id and r.status != 'cancelled':
                if exclude_id and r.id == exclude_id:
                    continue
                if r.start_time < end_time and r.end_time > start_time:
                    return True
        return False


@pytest.fixture
def service():
    return ReservationService(FakeReservationRepo())


@pytest.fixture
def now():
    return datetime.utcnow()


def test_create_success(service, now):
    reservation = service.create(
        user_id=1, provider_id=1, start_time=now, end_time=now + timedelta(hours=2),
        space_id=1, total_price=200,
    )
    assert reservation.id == 1
    assert reservation.user_id == 1
    assert reservation.status == 'pending'


def test_create_missing_time(service):
    with pytest.raises(ValueError):
        service.create(user_id=1, provider_id=1, start_time=None, end_time=None)


def test_create_end_before_start(service, now):
    with pytest.raises(ValueError):
        service.create(
            user_id=1, provider_id=1,
            start_time=now + timedelta(hours=2), end_time=now,
        )


def test_create_overlap(service, now):
    service.create(
        user_id=1, provider_id=1, start_time=now, end_time=now + timedelta(hours=2),
        space_id=1,
    )
    with pytest.raises(ValueError, match='already booked'):
        service.create(
            user_id=2, provider_id=1, start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=3), space_id=1,
        )


def test_get_success(service, now):
    service.create(user_id=1, provider_id=1, start_time=now, end_time=now + timedelta(hours=2))
    result = service.get(1)
    assert result is not None


def test_get_not_found(service):
    assert service.get(999) is None


def test_list(service, now):
    service.create(user_id=1, provider_id=1, start_time=now, end_time=now + timedelta(hours=2))
    service.create(user_id=2, provider_id=1, start_time=now, end_time=now + timedelta(hours=2))
    assert len(service.list()) == 2


def test_list_filter_user(service, now):
    service.create(user_id=1, provider_id=1, start_time=now, end_time=now + timedelta(hours=2))
    service.create(user_id=2, provider_id=1, start_time=now, end_time=now + timedelta(hours=2))
    assert len(service.list(user_id=1)) == 1


def test_list_invalid_status(service):
    with pytest.raises(ValueError):
        service.list(status='invalid')


def test_delete(service, now):
    service.create(user_id=1, provider_id=1, start_time=now, end_time=now + timedelta(hours=2))
    service.delete(1)
    assert service.get(1) is None


def test_delete_not_found(service):
    with pytest.raises(ValueError):
        service.delete(999)


def test_approve(service, now):
    service.create(user_id=1, provider_id=1, start_time=now, end_time=now + timedelta(hours=2))
    result = service.approve(1)
    assert result.status == 'approved'


def test_confirm(service, now):
    service.create(user_id=1, provider_id=1, start_time=now, end_time=now + timedelta(hours=2))
    service.approve(1)
    result = service.confirm(1)
    assert result.status == 'confirmed'


def test_cancel(service, now):
    service.create(user_id=1, provider_id=1, start_time=now, end_time=now + timedelta(hours=2))
    result = service.cancel(1)
    assert result.status == 'cancelled'


def test_invalid_transition(service, now):
    service.create(user_id=1, provider_id=1, start_time=now, end_time=now + timedelta(hours=2))
    with pytest.raises(ValueError, match='Cannot transition'):
        service.confirm(1)


def test_add_item(service, now):
    service.create(user_id=1, provider_id=1, start_time=now, end_time=now + timedelta(hours=2))
    item = service.add_item(1, item_type='space', item_id=1, quantity=1, price_at_booking=100)
    assert item.id == 1
    assert item.reservation_id == 1


def test_list_items(service, now):
    service.create(user_id=1, provider_id=1, start_time=now, end_time=now + timedelta(hours=2))
    service.add_item(1, item_type='space', item_id=1)
    service.add_item(1, item_type='resource', item_id=2)
    assert len(service.list_items(1)) == 2


def test_create_payment(service, now):
    service.create(user_id=1, provider_id=1, start_time=now, end_time=now + timedelta(hours=2))
    payment = service.create_payment(1, user_id=1, amount=200, method='cash')
    assert payment.id == 1
    assert payment.status == 'pending'


def test_create_payment_invalid_method(service, now):
    service.create(user_id=1, provider_id=1, start_time=now, end_time=now + timedelta(hours=2))
    with pytest.raises(ValueError):
        service.create_payment(1, user_id=1, amount=200, method='bitcoin')


def test_confirm_payment(service, now):
    service.create(user_id=1, provider_id=1, start_time=now, end_time=now + timedelta(hours=2))
    payment = service.create_payment(1, user_id=1, amount=200, method='cash')
    result = service.confirm_payment(payment.id)
    assert result.status == 'success'


def test_check_in(service, now):
    service.create(user_id=1, provider_id=1, start_time=now, end_time=now + timedelta(hours=2))
    service.approve(1)
    service.confirm(1)
    session = service.check_in(1)
    assert session.checked_in_at is not None


def test_check_in_invalid_status(service, now):
    service.create(user_id=1, provider_id=1, start_time=now, end_time=now + timedelta(hours=2))
    with pytest.raises(ValueError, match='must be confirmed'):
        service.check_in(1)


def test_check_out(service, now):
    service.create(user_id=1, provider_id=1, start_time=now, end_time=now + timedelta(hours=2))
    service.approve(1)
    service.confirm(1)
    service.check_in(1)
    session = service.check_out(1)
    assert session.status == 'completed'


def test_add_review(service, now):
    service.create(user_id=1, provider_id=1, start_time=now, end_time=now + timedelta(hours=2))
    review = service.add_review(1, user_id=1, rating=5, space_id=1, comment='Great!')
    assert review.rating == 5


def test_add_review_invalid_rating(service, now):
    service.create(user_id=1, provider_id=1, start_time=now, end_time=now + timedelta(hours=2))
    with pytest.raises(ValueError):
        service.add_review(1, user_id=1, rating=6)


def test_reservation_statuses():
    assert 'pending' in RESERVATION_STATUSES
    assert 'completed' in RESERVATION_STATUSES
    assert 'cancelled' in RESERVATION_STATUSES
