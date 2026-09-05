from flask import Blueprint, request, jsonify
from datetime import datetime
from api.pagination import paginate_list
from api.schemas.equipment import (
    PackageBookingRequestSchema, PackageBookingResponseSchema, ResourceConflictSchema,
)
from database.repositories.package_booking_repository import PackageBookingRepository
from services.package_booking_service import PackageBookingService


def _parse_datetime(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            from datetime import timezone
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    return value

bp = Blueprint('package_booking', __name__, url_prefix='/api/v1/package-bookings')

booking_service = PackageBookingService(PackageBookingRepository())
request_schema = PackageBookingRequestSchema()
response_schema = PackageBookingResponseSchema()
conflict_schema = ResourceConflictSchema()


@bp.route('', methods=['GET'])
def list_bookings():
    """
    List package bookings
    ---
    get:
      summary: List package bookings with optional filters
      tags: [Package Bookings]
      parameters:
        - name: package_id
          in: query
          schema: {type: integer}
        - name: customer_id
          in: query
          schema: {type: integer}
        - name: status
          in: query
          schema: {type: string, enum: [pending, confirmed, cancelled, completed]}
      responses:
        200:
          description: List of bookings
    """
    filters = {}
    for key in ('package_id', 'customer_id', 'status'):
        val = request.args.get(key)
        if val is not None:
            filters[key] = int(val) if key != 'status' else val
    items = booking_service.list(filters)
    return jsonify(paginate_list(items, response_schema)), 200


@bp.route('/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    """
    Get booking by ID
    ---
    get:
      summary: Get package booking by ID
      tags: [Package Bookings]
      parameters:
        - name: booking_id
          in: path
          required: true
          schema: {type: integer}
      responses:
        200:
          description: Booking object
        404:
          description: Not found
    """
    item = booking_service.get(booking_id)
    if not item:
        return jsonify({'message': 'Booking not found'}), 404
    return jsonify(response_schema.dump(item)), 200


@bp.route('', methods=['POST'])
def create_booking():
    """
    Create a package booking with resource availability check
    ---
    post:
      summary: Create a new package booking (validates resource availability)
      tags: [Package Bookings]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PackageBookingRequest'
      responses:
        201:
          description: Booking created
        400:
          description: Validation error
        409:
          description: Resource conflict
    """
    data = request.get_json()
    errors = request_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        item = booking_service.create(
            package_id=data['package_id'],
            space_id=data['space_id'],
            customer_id=data['customer_id'],
            start_time=_parse_datetime(data['start_time']),
            end_time=_parse_datetime(data['end_time']),
            notes=data.get('notes'),
        )
    except ValueError as e:
        msg = str(e)
        if 'Resource conflict' in msg:
            return jsonify({'message': msg, 'conflicts': []}), 409
        return jsonify({'message': msg}), 400
    return jsonify(response_schema.dump(item)), 201


@bp.route('/<int:booking_id>/cancel', methods=['PATCH'])
def cancel_booking(booking_id):
    """
    Cancel a package booking
    ---
    patch:
      summary: Cancel a package booking
      tags: [Package Bookings]
      parameters:
        - name: booking_id
          in: path
          required: true
          schema: {type: integer}
      responses:
        200:
          description: Booking cancelled
        400:
          description: Cannot cancel
        404:
          description: Not found
    """
    try:
        item = booking_service.cancel(booking_id)
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(response_schema.dump(item)), 200
