from flask import Blueprint, request, jsonify
from services.provider_service import ProviderService
from database.repositories.provider_profile_repository import ProviderProfileRepository
from api.schemas.provider import ProviderRequestSchema, ProviderResponseSchema

bp = Blueprint('provider', __name__, url_prefix='/providers')

provider_service = ProviderService(ProviderProfileRepository())
request_schema = ProviderRequestSchema()
response_schema = ProviderResponseSchema()


@bp.route('/', methods=['GET'])
def list_providers():
    """
    Get all provider profiles
    ---
    get:
      summary: Get all provider profiles
      tags:
        - Providers
      responses:
        200:
          description: List of provider profiles
    """
    providers = provider_service.list()
    return jsonify(response_schema.dump(providers, many=True)), 200


@bp.route('/<int:profile_id>', methods=['GET'])
def get_provider(profile_id):
    """
    Get provider profile by id
    ---
    get:
      summary: Get provider profile by id
      parameters:
        - name: profile_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Providers
      responses:
        200:
          description: Provider profile object
        404:
          description: Provider profile not found
    """
    provider = provider_service.get(profile_id)
    if not provider:
        return jsonify({'message': 'Provider profile not found'}), 404
    return jsonify(response_schema.dump(provider)), 200


@bp.route('/user/<int:user_id>', methods=['GET'])
def get_provider_by_user(user_id):
    """
    Get provider profile by user_id
    ---
    get:
      summary: Get provider profile by user_id
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Providers
      responses:
        200:
          description: Provider profile object
        404:
          description: Provider profile not found
    """
    provider = provider_service.get_by_user_id(user_id)
    if not provider:
        return jsonify({'message': 'Provider profile not found'}), 404
    return jsonify(response_schema.dump(provider)), 200


@bp.route('/', methods=['POST'])
def create_provider():
    """
    Create a new provider profile
    ---
    post:
      summary: Register as a provider
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ProviderRequest'
      tags:
        - Providers
      responses:
        201:
          description: Provider profile created
        400:
          description: Validation error
        409:
          description: User already has provider profile
    """
    data = request.get_json()
    errors = request_schema.validate(data)
    if errors:
        return jsonify({'message': 'Validation error', 'errors': errors}), 400
    try:
        provider = provider_service.create(
            user_id=data['user_id'],
            business_name=data['business_name'],
            description=data.get('description'),
            address=data.get('address')
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 409
    return jsonify(response_schema.dump(provider)), 201


@bp.route('/<int:profile_id>/approve', methods=['PUT'])
def approve_provider(profile_id):
    """
    Approve a provider profile (admin only)
    ---
    put:
      summary: Approve a provider profile
      parameters:
        - name: profile_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Providers
      responses:
        200:
          description: Provider approved
        404:
          description: Provider profile not found
    """
    try:
        provider = provider_service.approve(profile_id)
    except ValueError as e:
        return jsonify({'message': str(e)}), 404
    return jsonify(response_schema.dump(provider)), 200


@bp.route('/<int:profile_id>/reject', methods=['PUT'])
def reject_provider(profile_id):
    """
    Reject a provider profile (admin only)
    ---
    put:
      summary: Reject a provider profile
      parameters:
        - name: profile_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Providers
      responses:
        200:
          description: Provider rejected
        404:
          description: Provider profile not found
    """
    try:
        provider = provider_service.reject(profile_id)
    except ValueError as e:
        return jsonify({'message': str(e)}), 404
    return jsonify(response_schema.dump(provider)), 200


@bp.route('/<int:profile_id>', methods=['DELETE'])
def delete_provider(profile_id):
    """
    Delete a provider profile
    ---
    delete:
      summary: Delete a provider profile
      parameters:
        - name: profile_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Providers
      responses:
        204:
          description: Provider profile deleted
        404:
          description: Provider profile not found
    """
    try:
        provider_service.delete(profile_id)
    except ValueError as e:
        return jsonify({'message': str(e)}), 404
    return '', 204
