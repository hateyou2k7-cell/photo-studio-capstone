from flask import Blueprint, request, jsonify
from api.pagination import paginate_list
from services.equipment_service import EquipmentService
from database.repositories.equipment_repository import EquipmentRepository
from api.schemas.equipment import EquipmentRequestSchema, EquipmentUpdateSchema, EquipmentResponseSchema
from api.auth_middleware import jwt_required, role_required

bp = Blueprint('equipment', __name__, url_prefix='/api/v1/equipment')

equipment_service = EquipmentService(EquipmentRepository())
request_schema = EquipmentRequestSchema()
update_schema = EquipmentUpdateSchema()
response_schema = EquipmentResponseSchema()


@bp.route('', methods=['GET'])
def list_equipment():
    """
    List all equipment with optional filters
    ---
    get:
      summary: List equipment
      tags: [Equipment]
      parameters:
        - name: type
          in: query
          schema: {type: string}
        - name: space_id
          in: query
          schema: {type: integer}
        - name: available
          in: query
          schema: {type: boolean}
        - name: q
          in: query
          schema: {type: string}
      responses:
        200:
          description: List of equipment
    """
    filters = {}
    for key in ('q', 'type', 'space_id', 'available'):
        val = request.args.get(key)
        if val is not None:
            if key == 'available':
                filters[key] = val.lower() in ('1', 'true', 'yes')
            elif key == 'space_id':
                filters[key] = int(val)
            else:
                filters[key] = val
    items = equipment_service.list(filters)
    return jsonify(paginate_list(items, response_schema)), 200


@bp.route('/<int:equipment_id>', methods=['GET'])
def get_equipment(equipment_id):
    """
    Get equipment by ID
    ---
    get:
      summary: Get equipment by ID
      tags: [Equipment]
      parameters:
        - name: equipment_id
          in: path
          required: true
          schema: {type: integer}
      responses:
        200:
          description: Equipment object
        404:
          description: Not found
    """
    item = equipment_service.get(equipment_id)
    if not item:
        return jsonify({'message': 'Equipment not found'}), 404
    return jsonify(response_schema.dump(item)), 200


@bp.route('', methods=['POST'])
@jwt_required
def create_equipment():
    """
    Create new equipment
    ---
    post:
      summary: Create new equipment
      tags: [Equipment]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/EquipmentRequest'
      responses:
        201:
          description: Created
        400:
          description: Validation error
    """
    role = getattr(request, 'current_user_role', None)
    if role not in ('admin', 'manager', 'provider'):
        return jsonify({'error': 'Role not allowed'}), 403

    data = request.get_json()
    errors = request_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    if role == 'provider':
        from database.databases.factory_database import FactoryDatabase
        from database.models.film_user_model import ProviderProfile
        session = FactoryDatabase.get_database('POSTGREE').session
        profile = session.query(ProviderProfile).filter_by(user_id=request.current_user_id).first()
        if not profile or profile.id != data.get('provider_id'):
            return jsonify({'error': 'You can only create equipment for your own provider profile'}), 403
    elif role == 'manager':
        from database.databases.factory_database import FactoryDatabase
        from database.models.film_user_model import ProviderProfile
        session = FactoryDatabase.get_database('POSTGREE').session
        profile = session.query(ProviderProfile).filter_by(user_id=request.current_user_id).first()
        if not profile or profile.id != data.get('provider_id'):
            return jsonify({'error': 'Manager can only create equipment for their own provider profile'}), 403

    try:
        item = equipment_service.create(
            provider_id=data['provider_id'],
            name=data['name'],
            equipment_type=data['type'],
            space_id=data.get('space_id'),
            model_name=data.get('model_name'),
            compatibility=data.get('compatibility'),
            condition=data.get('condition', 'good'),
            description=data.get('description'),
            price_per_hour=data.get('price_per_hour', 0),
            is_available=data.get('is_available', True),
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(response_schema.dump(item)), 201


@bp.route('/<int:equipment_id>', methods=['PUT'])
@jwt_required
@role_required('admin', 'manager')
def update_equipment(equipment_id):
    """
    Update equipment
    ---
    put:
      summary: Update equipment
      tags: [Equipment]
      parameters:
        - name: equipment_id
          in: path
          required: true
          schema: {type: integer}
      responses:
        200:
          description: Updated
        400:
          description: Validation error
        404:
          description: Not found
    """
    data = request.get_json()
    errors = update_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        update_kwargs = {}
        if 'name' in data:
            update_kwargs['name'] = data['name']
        if 'model_name' in data:
            update_kwargs['model_name'] = data['model_name']
        if 'type' in data:
            update_kwargs['equipment_type'] = data['type']
        if 'compatibility' in data:
            update_kwargs['compatibility'] = data['compatibility']
        if 'condition' in data:
            update_kwargs['condition'] = data['condition']
        if 'description' in data:
            update_kwargs['description'] = data['description']
        if 'price_per_hour' in data:
            update_kwargs['price_per_hour'] = data['price_per_hour']
        if 'is_available' in data:
            update_kwargs['is_available'] = data['is_available']
        if 'space_id' in data:
            update_kwargs['space_id'] = data['space_id']
        item = equipment_service.update(equipment_id, **update_kwargs)
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(response_schema.dump(item)), 200


@bp.route('/<int:equipment_id>', methods=['DELETE'])
@jwt_required
@role_required('admin', 'manager')
def delete_equipment(equipment_id):
    """
    Delete equipment
    ---
    delete:
      summary: Delete equipment
      tags: [Equipment]
      parameters:
        - name: equipment_id
          in: path
          required: true
          schema: {type: integer}
      responses:
        204:
          description: Deleted
        404:
          description: Not found
    """
    try:
        equipment_service.delete(equipment_id)
    except ValueError as e:
        return jsonify({'message': str(e)}), 404
    return '', 204
