from flask import Blueprint, request, jsonify
from datetime import datetime
from api.auth_middleware import jwt_required
from api.pagination import paginate_list
from services.reservation_service import ReservationService
from infrastructure.repositories.reservation_repository import ReservationRepository
from api.schemas.reservation import (
    ReservationRequestSchema, ReservationResponseSchema,
    ReservationItemRequestSchema, ReservationItemResponseSchema,
    PaymentRequestSchema, PaymentResponseSchema,
    ServiceSessionResponseSchema,
    ReviewRequestSchema, ReviewResponseSchema,
)


def _parse_datetime(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    return value

bp = Blueprint('reservation', __name__, url_prefix='/v1/reservations')

reservation_service = ReservationService(ReservationRepository())
request_schema = ReservationRequestSchema()
response_schema = ReservationResponseSchema()
item_request_schema = ReservationItemRequestSchema()
item_response_schema = ReservationItemResponseSchema()
payment_request_schema = PaymentRequestSchema()
payment_response_schema = PaymentResponseSchema()
session_response_schema = ServiceSessionResponseSchema()
review_request_schema = ReviewRequestSchema()
review_response_schema = ReviewResponseSchema()


@bp.route('/', methods=['GET'])
def list_reservations():
    """
    List reservations with optional filters
    ---
    get:
      summary: List reservations (filter by user_id, provider_id, status)
      parameters:
        - name: user_id
          in: query
          schema:
            type: integer
        - name: provider_id
          in: query
          schema:
            type: integer
        - name: status
          in: query
          schema:
            type: string
            enum: [pending, approved, confirmed, checked_in, checked_out, completed, cancelled]
      tags:
        - Reservations
      responses:
        200:
          description: List of reservations
    """
    user_id = request.args.get('user_id', type=int)
    provider_id = request.args.get('provider_id', type=int)
    status = request.args.get('status')
    try:
        reservations = reservation_service.list(user_id=user_id, provider_id=provider_id, status=status)
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(paginate_list(reservations, response_schema)), 200


@bp.route('/<int:reservation_id>', methods=['GET'])
def get_reservation(reservation_id):
    """
    Get reservation by ID
    ---
    get:
      summary: Get a reservation by ID
      parameters:
        - name: reservation_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Reservations
      responses:
        200:
          description: Reservation object
        404:
          description: Not found
    """
    reservation = reservation_service.get(reservation_id)
    if not reservation:
        return jsonify({'message': 'Reservation not found'}), 404
    return jsonify(response_schema.dump(reservation)), 200


@bp.route('/', methods=['POST'])
@jwt_required
def create_reservation():
    """
    Create a new reservation
    ---
    post:
      summary: Create a new reservation
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ReservationRequest'
      tags:
        - Reservations
      responses:
        201:
          description: Created
        400:
          description: Invalid input
    """
    data = request.get_json()
    errors = request_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        start_time = _parse_datetime(data['start_time'])
        end_time = _parse_datetime(data['end_time'])
        reservation = reservation_service.create(
            user_id=data['user_id'],
            provider_id=data['provider_id'],
            start_time=start_time,
            end_time=end_time,
            space_id=data.get('space_id'),
            package_id=data.get('package_id'),
            total_price=data.get('total_price', 0),
            status=data.get('status', 'pending'),
            qr_code=data.get('qr_code'),
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(response_schema.dump(reservation)), 201


@bp.route('/<int:reservation_id>', methods=['PUT'])
@jwt_required
def update_reservation(reservation_id):
    """
    Update a reservation
    ---
    put:
      summary: Update a reservation by ID
      parameters:
        - name: reservation_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ReservationRequest'
      tags:
        - Reservations
      responses:
        200:
          description: Updated
        400:
          description: Invalid input
        404:
          description: Not found
    """
    existing = reservation_service.get(reservation_id)
    if not existing:
        return jsonify({'message': 'Reservation not found'}), 404
    data = request.get_json()
    errors = request_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        start_time = _parse_datetime(data['start_time'])
        end_time = _parse_datetime(data['end_time'])
        reservation = reservation_service.update(
            reservation_id=reservation_id,
            user_id=data['user_id'],
            provider_id=data['provider_id'],
            start_time=start_time,
            end_time=end_time,
            space_id=data.get('space_id'),
            package_id=data.get('package_id'),
            total_price=data.get('total_price', 0),
            status=data.get('status', 'pending'),
            qr_code=data.get('qr_code'),
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(response_schema.dump(reservation)), 200


@bp.route('/<int:reservation_id>', methods=['DELETE'])
@jwt_required
def delete_reservation(reservation_id):
    """
    Delete a reservation
    ---
    delete:
      summary: Delete a reservation by ID
      parameters:
        - name: reservation_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Reservations
      responses:
        204:
          description: Deleted
        404:
          description: Not found
    """
    existing = reservation_service.get(reservation_id)
    if not existing:
        return jsonify({'message': 'Reservation not found'}), 404
    reservation_service.delete(reservation_id)
    return '', 204


@bp.route('/<int:reservation_id>/approve', methods=['POST'])
@jwt_required
def approve_reservation(reservation_id):
    """
    Approve a reservation
    ---
    post:
      summary: Approve a pending reservation
      parameters:
        - name: reservation_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Reservations
      responses:
        200:
          description: Approved
        400:
          description: Invalid transition
    """
    try:
        reservation = reservation_service.approve(reservation_id)
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(response_schema.dump(reservation)), 200


@bp.route('/<int:reservation_id>/confirm', methods=['POST'])
@jwt_required
def confirm_reservation(reservation_id):
    """
    Confirm a reservation
    ---
    post:
      summary: Confirm an approved reservation
      parameters:
        - name: reservation_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Reservations
      responses:
        200:
          description: Confirmed
        400:
          description: Invalid transition
    """
    try:
        reservation = reservation_service.confirm(reservation_id)
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(response_schema.dump(reservation)), 200


@bp.route('/<int:reservation_id>/cancel', methods=['POST'])
@jwt_required
def cancel_reservation(reservation_id):
    """
    Cancel a reservation
    ---
    post:
      summary: Cancel a reservation
      parameters:
        - name: reservation_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Reservations
      responses:
        200:
          description: Cancelled
        400:
          description: Invalid transition
    """
    try:
        reservation = reservation_service.cancel(reservation_id)
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(response_schema.dump(reservation)), 200


@bp.route('/<int:reservation_id>/checkin', methods=['POST'])
@jwt_required
def check_in(reservation_id):
    """
    Check in to a reservation
    ---
    post:
      summary: Check in (creates or updates service session)
      parameters:
        - name: reservation_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Reservations
      responses:
        200:
          description: Checked in
        400:
          description: Invalid state
    """
    try:
        session = reservation_service.check_in(reservation_id)
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(session_response_schema.dump(session)), 200


@bp.route('/<int:reservation_id>/checkout', methods=['POST'])
@jwt_required
def check_out(reservation_id):
    """
    Check out from a reservation
    ---
    post:
      summary: Check out (completes service session, calculates duration)
      parameters:
        - name: reservation_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Reservations
      responses:
        200:
          description: Checked out
        400:
          description: Invalid state
    """
    try:
        session = reservation_service.check_out(reservation_id)
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(session_response_schema.dump(session)), 200


@bp.route('/<int:reservation_id>/items', methods=['GET'])
def list_items(reservation_id):
    """
    List items for a reservation
    ---
    get:
      summary: List reservation items
      parameters:
        - name: reservation_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Reservations
      responses:
        200:
          description: List of items
    """
    items = reservation_service.list_items(reservation_id)
    return jsonify(item_response_schema.dump(items, many=True)), 200


@bp.route('/<int:reservation_id>/items', methods=['POST'])
def add_item(reservation_id):
    """
    Add an item to a reservation
    ---
    post:
      summary: Add a reservation item (space/resource/consumable)
      parameters:
        - name: reservation_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ReservationItemRequest'
      tags:
        - Reservations
      responses:
        201:
          description: Created
        400:
          description: Invalid input
    """
    data = request.get_json()
    errors = item_request_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        item = reservation_service.add_item(
            reservation_id=reservation_id,
            item_type=data['item_type'],
            item_id=data['item_id'],
            quantity=data.get('quantity', 1),
            price_at_booking=data.get('price_at_booking', 0),
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(item_response_schema.dump(item)), 201


@bp.route('/<int:reservation_id>/payment', methods=['GET'])
def get_payment(reservation_id):
    """
    Get payment for a reservation
    ---
    get:
      summary: Get payment info
      parameters:
        - name: reservation_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Reservations
      responses:
        200:
          description: Payment object
        404:
          description: No payment found
    """
    payment = reservation_service.get_payment(reservation_id)
    if not payment:
        return jsonify({'message': 'No payment found'}), 404
    return jsonify(payment_response_schema.dump(payment)), 200


@bp.route('/<int:reservation_id>/payment', methods=['POST'])
@jwt_required
def create_payment(reservation_id):
    """
    Create a payment for a reservation
    ---
    post:
      summary: Create a payment record
      parameters:
        - name: reservation_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PaymentRequest'
      tags:
        - Reservations
      responses:
        201:
          description: Created
        400:
          description: Invalid input
    """
    data = request.get_json()
    errors = payment_request_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        payment = reservation_service.create_payment(
            reservation_id=reservation_id,
            user_id=data['user_id'],
            amount=data['amount'],
            method=data['method'],
            transaction_ref=data.get('transaction_ref'),
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(payment_response_schema.dump(payment)), 201


@bp.route('/<int:reservation_id>/payment/confirm', methods=['POST'])
@jwt_required
def confirm_payment(reservation_id):
    """
    Confirm payment (mark as success)
    ---
    post:
      summary: Mark payment as successful
      parameters:
        - name: reservation_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Reservations
      responses:
        200:
          description: Payment confirmed
        404:
          description: No payment found
    """
    payment = reservation_service.get_payment(reservation_id)
    if not payment:
        return jsonify({'message': 'No payment found'}), 404
    try:
        payment = reservation_service.confirm_payment(payment.id)
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(payment_response_schema.dump(payment)), 200


@bp.route('/<int:reservation_id>/reviews', methods=['GET'])
def list_reviews(reservation_id):
    """
    List reviews (by space_id from reservation)
    ---
    get:
      summary: List reviews for the space of this reservation
      parameters:
        - name: reservation_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Reservations
      responses:
        200:
          description: List of reviews
    """
    reservation = reservation_service.get(reservation_id)
    if not reservation:
        return jsonify({'message': 'Reservation not found'}), 404
    space_id = reservation.space_id
    if not space_id:
        return jsonify([]), 200
    reviews = reservation_service.list_reviews(space_id)
    return jsonify(review_response_schema.dump(reviews, many=True)), 200


@bp.route('/<int:reservation_id>/reviews', methods=['POST'])
@jwt_required
def add_review(reservation_id):
    """
    Add a review for a reservation
    ---
    post:
      summary: Add a review after completed reservation
      parameters:
        - name: reservation_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ReviewRequest'
      tags:
        - Reservations
      responses:
        201:
          description: Created
        400:
          description: Invalid input
    """
    data = request.get_json()
    errors = review_request_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        reservation = reservation_service.get(reservation_id)
        if not reservation:
            return jsonify({'message': 'Reservation not found'}), 404
        review = reservation_service.add_review(
            reservation_id=reservation_id,
            user_id=data['user_id'],
            rating=data['rating'],
            space_id=data.get('space_id', reservation.space_id),
            comment=data.get('comment'),
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(review_response_schema.dump(review)), 201
