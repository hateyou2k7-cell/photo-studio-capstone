from flask import Blueprint, request, jsonify
from services.room_service import RoomService
from infrastructure.repositories.room_repository import RoomRepository
from api.schemas.room import RoomRequestSchema, RoomResponseSchema
from datetime import datetime

bp = Blueprint('room', __name__, url_prefix='/rooms')

room_service = RoomService(RoomRepository())
request_schema = RoomRequestSchema()
response_schema = RoomResponseSchema()


@bp.route('/', methods=['GET'])
def list_rooms():
    """
    Get all rooms
    ---
    get:
      summary: Get all rooms
      tags:
        - Rooms
      responses:
        200:
          description: List of rooms
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/RoomResponse'
    """
    rooms = room_service.list_rooms()
    return jsonify(response_schema.dump(rooms, many=True)), 200


@bp.route('/<int:room_id>', methods=['GET'])
def get_room(room_id):
    """
    Get room by id
    ---
    get:
      summary: Get room by id
      parameters:
        - name: room_id
          in: path
          required: true
          schema:
            type: integer
          description: ID của room cần lấy
      tags:
        - Rooms
      responses:
        200:
          description: object of room
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RoomResponse'
        404:
          description: Room not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    room = room_service.get_room(room_id)
    if not room:
        return jsonify({'message': 'Room not found'}), 404
    return jsonify(response_schema.dump(room)), 200


@bp.route('/', methods=['POST'])
def create_room():
    """
    Create a new room
    ---
    post:
      summary: Create a new room
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RoomRequest'
      tags:
        - Rooms
      responses:
        201:
          description: Room created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RoomResponse'
        400:
          description: Invalid input
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
    """
    data = request.get_json()
    errors = request_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    now = datetime.utcnow()
    room = room_service.create_room(
        name=data['name'],
        description=data.get('description'),
        room_type=data.get('room_type', 'standard'),
        capacity=data.get('capacity', 1),
        price_per_hour=data.get('price_per_hour', 0),
        status=data.get('status', 'available'),
        created_at=now,
        updated_at=now
    )
    return jsonify(response_schema.dump(room)), 201


@bp.route('/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    """
    Update a room by id
    ---
    put:
      summary: Update a room by id
      parameters:
        - name: room_id
          in: path
          required: true
          schema:
            type: integer
          description: ID của room cần cập nhật
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RoomRequest'
      tags:
        - Rooms
      responses:
        200:
          description: Room updated successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RoomResponse'
        400:
          description: Invalid input
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
        404:
          description: Room not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    existing = room_service.get_room(room_id)
    if not existing:
        return jsonify({'message': 'Room not found'}), 404
    data = request.get_json()
    errors = request_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    room = room_service.update_room(
        room_id=room_id,
        name=data['name'],
        description=data.get('description'),
        room_type=data.get('room_type', 'standard'),
        capacity=data.get('capacity', 1),
        price_per_hour=data.get('price_per_hour', 0),
        status=data.get('status', 'available'),
        created_at=existing.created_at,
        updated_at=datetime.utcnow()
    )
    return jsonify(response_schema.dump(room)), 200


@bp.route('/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    """
    Delete a room by id
    ---
    delete:
      summary: Delete a room by id
      parameters:
        - name: room_id
          in: path
          required: true
          schema:
            type: integer
          description: ID của room cần xóa
      tags:
        - Rooms
      responses:
        204:
          description: Room deleted successfully
        404:
          description: Room not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    existing = room_service.get_room(room_id)
    if not existing:
        return jsonify({'message': 'Room not found'}), 404
    room_service.delete_room(room_id)
    return '', 204