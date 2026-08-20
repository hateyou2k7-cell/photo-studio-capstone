from flask import Blueprint, request, jsonify
from services.space_image_service import SpaceImageService
from infrastructure.repositories.space_image_repository import SpaceImageRepository
from api.schemas.space_image import SpaceImageResponseSchema, SpaceImagePrimaryRequestSchema

bp = Blueprint('space_image', __name__, url_prefix='/spaces')

image_service = SpaceImageService(SpaceImageRepository())
response_schema = SpaceImageResponseSchema()
primary_schema = SpaceImagePrimaryRequestSchema()


@bp.route('/<int:space_id>/images', methods=['POST'])
def upload_images(space_id):
    """
    Upload multiple images for a space
    ---
    post:
      summary: Upload multiple images for a space (multipart/form-data, field name "images")
      parameters:
        - name: space_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                images:
                  type: array
                  items:
                    type: string
                    format: binary
      tags:
        - Space Images
      responses:
        201:
          description: Images uploaded successfully
        400:
          description: Invalid input
    """
    files = request.files.getlist('images')
    if not files:
        return jsonify({'message': 'No images provided'}), 400
    try:
        images = image_service.add_images(space_id, files)
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(response_schema.dump(images, many=True)), 201


@bp.route('/<int:space_id>/images', methods=['GET'])
def list_images(space_id):
    """
    List all images of a space
    ---
    get:
      summary: List all images of a space
      parameters:
        - name: space_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Space Images
      responses:
        200:
          description: List of images
    """
    images = image_service.list_images(space_id)
    return jsonify(response_schema.dump(images, many=True)), 200


@bp.route('/<int:space_id>/images/<int:image_id>', methods=['PUT'])
def update_image(space_id, image_id):
    """
    Set primary image for a space
    ---
    put:
      summary: Set primary image for a space
      parameters:
        - name: space_id
          in: path
          required: true
          schema:
            type: integer
        - name: image_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                is_primary:
                  type: boolean
      tags:
        - Space Images
      responses:
        200:
          description: Image updated
        400:
          description: Invalid input
        404:
          description: Image not found
    """
    data = request.get_json()
    errors = primary_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        image = image_service.set_primary(space_id, image_id)
    except ValueError as e:
        return jsonify({'message': str(e)}), 404
    return jsonify(response_schema.dump(image)), 200


@bp.route('/<int:space_id>/images/<int:image_id>', methods=['DELETE'])
def delete_image(space_id, image_id):
    """
    Delete an image of a space
    ---
    delete:
      summary: Delete an image of a space
      parameters:
        - name: space_id
          in: path
          required: true
          schema:
            type: integer
        - name: image_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Space Images
      responses:
        204:
          description: Image deleted
        404:
          description: Image not found
    """
    try:
        image_service.delete_image(space_id, image_id)
    except ValueError as e:
        return jsonify({'message': str(e)}), 404
    return '', 204