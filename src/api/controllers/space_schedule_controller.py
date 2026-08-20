from flask import Blueprint, request, jsonify
from datetime import datetime
from services.space_schedule_service import SpaceScheduleService
from infrastructure.repositories.space_schedule_repository import SpaceScheduleRepository
from api.schemas.space_schedule import SpaceScheduleRequestSchema, SpaceScheduleResponseSchema

bp = Blueprint('space_schedule', __name__, url_prefix='/spaces')

schedule_service = SpaceScheduleService(SpaceScheduleRepository())
request_schema = SpaceScheduleRequestSchema()
response_schema = SpaceScheduleResponseSchema()


def parse_time(value):
    try:
        return datetime.strptime(value, '%H:%M').time()
    except ValueError:
        try:
            return datetime.strptime(value, '%H:%M:%S').time()
        except ValueError:
            raise ValueError('Invalid time format, expected HH:MM')


def build_payload(data, space_id, schedule_id=None):
    day_of_week = data['day_of_week']
    start_time = parse_time(data['start_time'])
    end_time = parse_time(data['end_time'])
    is_available = data.get('is_available', True)
    return schedule_id, space_id, day_of_week, start_time, end_time, is_available


@bp.route('/<int:space_id>/schedule', methods=['GET'])
def list_schedule(space_id):
    """
    List operating schedule of a space
    ---
    get:
      summary: List operating schedule (time slots) of a space
      parameters:
        - name: space_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Space Schedule
      responses:
        200:
          description: List of schedule slots
    """
    slots = schedule_service.list(space_id)
    return jsonify(response_schema.dump(slots, many=True)), 200


@bp.route('/<int:space_id>/schedule', methods=['POST'])
def create_slot(space_id):
    """
    Add an operating time slot for a space
    ---
    post:
      summary: Add an operating time slot for a space
      parameters:
        - name: space_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SpaceScheduleRequest'
      tags:
        - Space Schedule
      responses:
        201:
          description: Schedule slot created
        400:
          description: Invalid input
    """
    data = request.get_json()
    errors = request_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        _, space_id, day_of_week, start_time, end_time, is_available = build_payload(data, space_id)
        slot = schedule_service.create(space_id, day_of_week, start_time, end_time, is_available)
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(response_schema.dump(slot)), 201


@bp.route('/<int:space_id>/schedule/<int:schedule_id>', methods=['PUT'])
def update_slot(space_id, schedule_id):
    """
    Update an operating time slot of a space
    ---
    put:
      summary: Update an operating time slot of a space
      parameters:
        - name: space_id
          in: path
          required: true
          schema:
            type: integer
        - name: schedule_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SpaceScheduleRequest'
      tags:
        - Space Schedule
      responses:
        200:
          description: Schedule slot updated
        400:
          description: Invalid input
        404:
          description: Schedule slot not found
    """
    data = request.get_json()
    errors = request_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        _, space_id, day_of_week, start_time, end_time, is_available = build_payload(data, space_id)
        slot = schedule_service.update(schedule_id, space_id, day_of_week, start_time, end_time, is_available)
    except ValueError as e:
        return jsonify({'message': str(e)}), 404
    return jsonify(response_schema.dump(slot)), 200


@bp.route('/<int:space_id>/schedule/<int:schedule_id>', methods=['DELETE'])
def delete_slot(space_id, schedule_id):
    """
    Delete an operating time slot of a space
    ---
    delete:
      summary: Delete an operating time slot of a space
      parameters:
        - name: space_id
          in: path
          required: true
          schema:
            type: integer
        - name: schedule_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Space Schedule
      responses:
        204:
          description: Schedule slot deleted
        404:
          description: Schedule slot not found
    """
    try:
        schedule_service.delete(space_id, schedule_id)
    except ValueError as e:
        return jsonify({'message': str(e)}), 404
    return '', 204