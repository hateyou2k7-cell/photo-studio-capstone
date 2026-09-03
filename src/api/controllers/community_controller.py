from flask import Blueprint, request, jsonify
from datetime import datetime
from api.auth_middleware import jwt_required, role_required
from api.pagination import paginate_list
from services.community_service import CommunityService
from database.repositories.post_repository import PostRepository
from database.repositories.workshop_repository import WorkshopRepository
from api.schemas.community import (
    PostRequestSchema, PostResponseSchema,
    CommentRequestSchema, CommentResponseSchema,
    WorkshopRequestSchema, WorkshopResponseSchema,
    WorkshopRegistrationRequestSchema, WorkshopRegistrationResponseSchema,
)


def _parse_datetime(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    return value


bp = Blueprint('community', __name__, url_prefix='/api/v1/community')

community_service = CommunityService(PostRepository(), WorkshopRepository())
post_request_schema = PostRequestSchema()
post_response_schema = PostResponseSchema()
comment_request_schema = CommentRequestSchema()
comment_response_schema = CommentResponseSchema()
workshop_request_schema = WorkshopRequestSchema()
workshop_response_schema = WorkshopResponseSchema()
reg_request_schema = WorkshopRegistrationRequestSchema()
reg_response_schema = WorkshopRegistrationResponseSchema()


# ==================== POSTS ====================

@bp.route('/posts', methods=['GET'])
def list_posts():
    """
    List posts with optional filters
    ---
    get:
      summary: List posts (filter by author_id, category)
      parameters:
        - name: author_id
          in: query
          schema:
            type: integer
        - name: category
          in: query
          schema:
            type: string
            enum: [article, tutorial, equipment_review, technique]
      tags:
        - Community
      responses:
        200:
          description: List of posts
    """
    author_id = request.args.get('author_id', type=int)
    category = request.args.get('category')
    posts = community_service.list_posts(author_id=author_id, category=category)
    return jsonify(paginate_list(posts, post_response_schema)), 200


@bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """
    Get post by ID (increments view count)
    ---
    get:
      summary: Get a post by ID
      parameters:
        - name: post_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Community
      responses:
        200:
          description: Post object
        404:
          description: Not found
    """
    post = community_service.get_post(post_id)
    if not post:
        return jsonify({'message': 'Post not found'}), 404
    return jsonify(post_response_schema.dump(post)), 200


@bp.route('/posts', methods=['POST'])
@jwt_required
@role_required('admin', 'manager')
def create_post():
    """
    Create a new post
    ---
    post:
      summary: Create a new post (article, tutorial, etc.)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PostRequest'
      tags:
        - Community
      responses:
        201:
          description: Created
        400:
          description: Invalid input
    """
    data = request.get_json()
    errors = post_request_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        author_id = getattr(request, 'current_user_id', None) or data.get('author_id')
        if not author_id:
            return jsonify({'message': 'author_id is required'}), 400
        post = community_service.create_post(
            author_id=author_id,
            title=data['title'],
            content=data['content'],
            category=data.get('category', 'article'),
            is_published=data.get('is_published', True),
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(post_response_schema.dump(post)), 201


@bp.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required
@role_required('admin', 'manager')
def update_post(post_id):
    """
    Update a post
    ---
    put:
      summary: Update a post by ID
      parameters:
        - name: post_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PostRequest'
      tags:
        - Community
      responses:
        200:
          description: Updated
        400:
          description: Invalid input
        404:
          description: Not found
    """
    existing = community_service.get_post(post_id)
    if not existing:
        return jsonify({'message': 'Post not found'}), 404
    data = request.get_json()
    errors = post_request_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        post = community_service.update_post(
            post_id=post_id,
            title=data['title'],
            content=data['content'],
            category=data.get('category', 'article'),
            is_published=data.get('is_published', True),
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(post_response_schema.dump(post)), 200


@bp.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required
@role_required('admin', 'manager')
def delete_post(post_id):
    """
    Delete a post
    ---
    delete:
      summary: Delete a post by ID
      parameters:
        - name: post_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Community
      responses:
        204:
          description: Deleted
        404:
          description: Not found
    """
    existing = community_service.get_post(post_id)
    if not existing:
        return jsonify({'message': 'Post not found'}), 404
    community_service.delete_post(post_id)
    return '', 204


# ==================== COMMENTS ====================

@bp.route('/posts/<int:post_id>/comments', methods=['GET'])
def list_comments(post_id):
    """
    List comments for a post
    ---
    get:
      summary: List comments
      parameters:
        - name: post_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Community
      responses:
        200:
          description: List of comments
    """
    try:
        comments = community_service.list_comments(post_id)
    except ValueError as e:
        return jsonify({'message': str(e)}), 404
    return jsonify(comment_response_schema.dump(comments, many=True)), 200


@bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required
def add_comment(post_id):
    """
    Add a comment to a post
    ---
    post:
      summary: Add a comment
      parameters:
        - name: post_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CommentRequest'
      tags:
        - Community
      responses:
        201:
          description: Created
        400:
          description: Invalid input
    """
    data = request.get_json()
    errors = comment_request_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        user_id = getattr(request, 'current_user_id', None) or data.get('user_id')
        if not user_id:
            return jsonify({'message': 'user_id is required'}), 400
        comment = community_service.add_comment(
            post_id=post_id,
            user_id=user_id,
            content=data['content'],
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(comment_response_schema.dump(comment)), 201


@bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required
@role_required('admin', 'manager')
def delete_comment(comment_id):
    """
    Delete a comment
    ---
    delete:
      summary: Delete a comment by ID
      parameters:
        - name: comment_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Community
      responses:
        204:
          description: Deleted
        404:
          description: Not found
    """
    try:
        community_service.delete_comment(comment_id)
    except ValueError as e:
        return jsonify({'message': str(e)}), 404
    return '', 204


# ==================== WORKSHOPS ====================

@bp.route('/workshops', methods=['GET'])
def list_workshops():
    """
    List workshops with optional filters
    ---
    get:
      summary: List workshops (filter by expert_id, status)
      parameters:
        - name: expert_id
          in: query
          schema:
            type: integer
        - name: status
          in: query
          schema:
            type: string
            enum: [open, full, cancelled, done]
      tags:
        - Community
      responses:
        200:
          description: List of workshops
    """
    expert_id = request.args.get('expert_id', type=int)
    status = request.args.get('status')
    workshops = community_service.list_workshops(expert_id=expert_id, status=status)
    return jsonify(paginate_list(workshops, workshop_response_schema)), 200


@bp.route('/workshops/<int:workshop_id>', methods=['GET'])
def get_workshop(workshop_id):
    """
    Get workshop by ID
    ---
    get:
      summary: Get a workshop by ID
      parameters:
        - name: workshop_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Community
      responses:
        200:
          description: Workshop object
        404:
          description: Not found
    """
    workshop = community_service.get_workshop(workshop_id)
    if not workshop:
        return jsonify({'message': 'Workshop not found'}), 404
    return jsonify(workshop_response_schema.dump(workshop)), 200


@bp.route('/workshops', methods=['POST'])
@jwt_required
@role_required('admin', 'manager')
def create_workshop():
    """
    Create a new workshop
    ---
    post:
      summary: Create a new workshop
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/WorkshopRequest'
      tags:
        - Community
      responses:
        201:
          description: Created
        400:
          description: Invalid input
    """
    data = request.get_json()
    errors = workshop_request_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        expert_id = getattr(request, 'current_user_id', None) or data.get('expert_id')
        if not expert_id:
            return jsonify({'message': 'expert_id is required'}), 400
        workshop = community_service.create_workshop(
            expert_id=expert_id,
            title=data['title'],
            scheduled_at=_parse_datetime(data['scheduled_at']),
            description=data.get('description'),
            location=data.get('location'),
            capacity=data.get('capacity', 10),
            price=data.get('price', 0),
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(workshop_response_schema.dump(workshop)), 201


@bp.route('/workshops/<int:workshop_id>', methods=['PUT'])
@jwt_required
@role_required('admin', 'manager')
def update_workshop(workshop_id):
    """
    Update a workshop
    ---
    put:
      summary: Update a workshop by ID
      parameters:
        - name: workshop_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/WorkshopRequest'
      tags:
        - Community
      responses:
        200:
          description: Updated
        400:
          description: Invalid input
        404:
          description: Not found
    """
    existing = community_service.get_workshop(workshop_id)
    if not existing:
        return jsonify({'message': 'Workshop not found'}), 404
    data = request.get_json()
    errors = workshop_request_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        workshop = community_service.update_workshop(
            workshop_id=workshop_id,
            title=data['title'],
            scheduled_at=_parse_datetime(data['scheduled_at']),
            description=data.get('description'),
            location=data.get('location'),
            capacity=data.get('capacity', 10),
            price=data.get('price', 0),
            status=data.get('status', 'open'),
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(workshop_response_schema.dump(workshop)), 200


@bp.route('/workshops/<int:workshop_id>', methods=['DELETE'])
@jwt_required
@role_required('admin', 'manager')
def delete_workshop(workshop_id):
    """
    Delete a workshop
    ---
    delete:
      summary: Delete a workshop by ID
      parameters:
        - name: workshop_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Community
      responses:
        204:
          description: Deleted
        404:
          description: Not found
    """
    existing = community_service.get_workshop(workshop_id)
    if not existing:
        return jsonify({'message': 'Workshop not found'}), 404
    community_service.delete_workshop(workshop_id)
    return '', 204


# ==================== WORKSHOP REGISTRATIONS ====================

@bp.route('/workshops/<int:workshop_id>/register', methods=['POST'])
@jwt_required
def register_workshop(workshop_id):
    """
    Register for a workshop
    ---
    post:
      summary: Register for a workshop
      parameters:
        - name: workshop_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/WorkshopRegistrationRequest'
      tags:
        - Community
      responses:
        201:
          description: Registered
        400:
          description: Invalid input or workshop full
    """
    data = request.get_json()
    errors = reg_request_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        user_id = getattr(request, 'current_user_id', None) or data.get('user_id')
        if not user_id:
            return jsonify({'message': 'user_id is required'}), 400
        reg = community_service.register_workshop(
            workshop_id=workshop_id,
            user_id=user_id,
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(reg_response_schema.dump(reg)), 201


@bp.route('/workshops/<int:workshop_id>/registrations', methods=['GET'])
def list_registrations(workshop_id):
    """
    List registrations for a workshop
    ---
    get:
      summary: List workshop registrations
      parameters:
        - name: workshop_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Community
      responses:
        200:
          description: List of registrations
    """
    try:
        regs = community_service.list_registrations(workshop_id)
    except ValueError as e:
        return jsonify({'message': str(e)}), 404
    return jsonify(reg_response_schema.dump(regs, many=True)), 200


@bp.route('/registrations/<int:registration_id>/cancel', methods=['POST'])
@jwt_required
def cancel_registration(registration_id):
    """
    Cancel a workshop registration
    ---
    post:
      summary: Cancel a registration
      parameters:
        - name: registration_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Community
      responses:
        200:
          description: Cancelled
        404:
          description: Not found
    """
    try:
        reg = community_service.cancel_registration(registration_id)
    except ValueError as e:
        return jsonify({'message': str(e)}), 404
    return jsonify(reg_response_schema.dump(reg)), 200
