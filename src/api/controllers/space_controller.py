from flask import Blueprint, request, jsonify
from api.pagination import paginate_list
from services.space_service import SpaceService
from database.repositories.space_repository import SpaceRepository
from api.schemas.space import SpaceRequestSchema, SpaceResponseSchema

bp = Blueprint('space', __name__, url_prefix='/spaces')

space_service = SpaceService(SpaceRepository())
request_schema = SpaceRequestSchema()
response_schema = SpaceResponseSchema()


@bp.route('/', methods=['GET'])
def list_spaces():
    """
    Get all spaces (rooms)
    ---
    get:
      summary: Get all spaces (rooms)
      tags:
        - Spaces
      responses:
        200:
          description: List of spaces
    """
    spaces = space_service.list()
    return jsonify(paginate_list(spaces, response_schema)), 200


@bp.route('/search', methods=['GET'])
def search_spaces():
    """
    Search spaces (rooms) with filters
    ---
    get:
      summary: Search spaces with filters (q, space_type, min_price, max_price, min_capacity, available)
      parameters:
        - name: q
          in: query
          required: false
          schema:
            type: string
          description: Text search on name, description, address
        - name: space_type
          in: query
          required: false
          schema:
            type: string
        - name: min_price
          in: query
          required: false
          schema:
            type: number
        - name: max_price
          in: query
          required: false
          schema:
            type: number
        - name: min_capacity
          in: query
          required: false
          schema:
            type: integer
        - name: available
          in: query
          required: false
          schema:
            type: boolean
      tags:
        - Spaces
      responses:
        200:
          description: List of matching spaces
        400:
          description: Invalid filter
    """
    filters = {}
    if request.args.get('q'):
        filters['q'] = request.args['q']
    if request.args.get('space_type'):
        filters['space_type'] = request.args['space_type']
    if request.args.get('min_price') is not None:
        filters['min_price'] = float(request.args['min_price'])
    if request.args.get('max_price') is not None:
        filters['max_price'] = float(request.args['max_price'])
    if request.args.get('min_capacity') is not None:
        filters['min_capacity'] = int(request.args['min_capacity'])
    if request.args.get('available') is not None:
        filters['available'] = request.args['available'].lower() in ('1', 'true', 'yes')
    try:
        spaces = space_service.search(filters)
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(paginate_list(spaces, response_schema)), 200


@bp.route('/<int:space_id>', methods=['GET'])
def get_space(space_id):
    """
    Get a space by id
    ---
    get:
      summary: Get a space (room) by id
      parameters:
        - name: space_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Spaces
      responses:
        200:
          description: object of space
        404:
          description: Space not found
    """
    space = space_service.get(space_id)
    if not space:
        return jsonify({'message': 'Space not found'}), 404
    return jsonify(response_schema.dump(space)), 200


@bp.route('/', methods=['POST'])
def create_space():
    """
    Create a new space (room)
    ---
    post:
      summary: Create a new space (room) for a provider
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SpaceRequest'
      tags:
        - Spaces
      responses:
        201:
          description: Space created successfully
        400:
          description: Invalid input
    """
    data = request.get_json()
    errors = request_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        space = space_service.create(
            provider_id=data['provider_id'],
            name=data['name'],
            space_type=data['space_type'],
            description=data.get('description'),
            address=data.get('address'),
            max_capacity=data.get('max_capacity'),
            base_price_per_hour=data.get('base_price_per_hour', 0),
            status=data.get('status', True)
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(response_schema.dump(space)), 201


@bp.route('/<int:space_id>', methods=['PUT'])
def update_space(space_id):
    """
    Update a space by id
    ---
    put:
      summary: Update a space (room) by id
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
              $ref: '#/components/schemas/SpaceRequest'
      tags:
        - Spaces
      responses:
        200:
          description: Space updated successfully
        400:
          description: Invalid input
        404:
          description: Space not found
    """
    existing = space_service.get(space_id)
    if not existing:
        return jsonify({'message': 'Space not found'}), 404
    data = request.get_json()
    errors = request_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        space = space_service.update(
            space_id=space_id,
            provider_id=data['provider_id'],
            name=data['name'],
            space_type=data['space_type'],
            description=data.get('description'),
            address=data.get('address'),
            max_capacity=data.get('max_capacity'),
            base_price_per_hour=data.get('base_price_per_hour', 0),
            status=data.get('status', True)
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(response_schema.dump(space)), 200


@bp.route('/<int:space_id>', methods=['DELETE'])
def delete_space(space_id):
    """
    Delete a space by id
    ---
    delete:
      summary: Delete a space (room) by id
      parameters:
        - name: space_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Spaces
      responses:
        204:
          description: Space deleted successfully
        404:
          description: Space not found
    """
    existing = space_service.get(space_id)
    if not existing:
        return jsonify({'message': 'Space not found'}), 404
    space_service.delete(space_id)
    return '', 204