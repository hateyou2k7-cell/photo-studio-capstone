from flask import Blueprint, request, jsonify
from services.course_service import CourseService
from infrastructure.repositories.course_repository import CourseRepository
from datetime import datetime

bp = Blueprint('course', __name__, url_prefix='/courses')

course_service = CourseService(CourseRepository())


@bp.route('/', methods=['GET'])
def list_courses():
    """
    Get all courses
    ---
    get:
      summary: Get all courses
      tags:
        - Courses
      responses:
        200:
          description: List of courses
    """
    courses = course_service.list_courses()
    result = []
    for c in courses:
        result.append({
            'id': c.id,
            'course_name': c.course_name,
            'description': c.description,
            'status': c.status,
            'start_date': str(c.start_date) if c.start_date else None,
            'end_date': str(c.end_date) if c.end_date else None,
            'created_at': str(c.created_at) if c.created_at else None,
            'updated_at': str(c.updated_at) if c.updated_at else None,
        })
    return jsonify(result), 200


@bp.route('/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """
    Get course by ID
    ---
    get:
      summary: Get a course by ID
      parameters:
        - name: course_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Courses
      responses:
        200:
          description: Course object
        404:
          description: Not found
    """
    course = course_service.get_course(course_id)
    if not course:
        return jsonify({'message': 'Course not found'}), 404
    return jsonify({
        'id': course.id,
        'course_name': course.course_name,
        'description': course.description,
        'status': course.status,
        'start_date': str(course.start_date) if course.start_date else None,
        'end_date': str(course.end_date) if course.end_date else None,
        'created_at': str(course.created_at) if course.created_at else None,
        'updated_at': str(course.updated_at) if course.updated_at else None,
    }), 200


@bp.route('/', methods=['POST'])
def create_course():
    """
    Create a new course
    ---
    post:
      summary: Create a new course
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [course_name, description, status]
              properties:
                course_name:
                  type: string
                description:
                  type: string
                status:
                  type: string
                start_date:
                  type: string
                end_date:
                  type: string
      tags:
        - Courses
      responses:
        201:
          description: Created
        400:
          description: Invalid input
    """
    data = request.get_json()
    if not data.get('course_name') or not data.get('description') or not data.get('status'):
        return jsonify({'message': 'Missing required fields: course_name, description, status'}), 400
    now = datetime.utcnow()
    course = course_service.create_course(
        course_name=data['course_name'],
        description=data['description'],
        status=data['status'],
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        created_at=now,
        updated_at=now,
    )
    return jsonify({
        'id': course.id,
        'course_name': course.course_name,
        'description': course.description,
        'status': course.status,
    }), 201


@bp.route('/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    """
    Update a course
    ---
    put:
      summary: Update a course by ID
      parameters:
        - name: course_id
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
              required: [course_name, description, status]
              properties:
                course_name:
                  type: string
                description:
                  type: string
                status:
                  type: string
      tags:
        - Courses
      responses:
        200:
          description: Updated
        400:
          description: Invalid input
        404:
          description: Not found
    """
    existing = course_service.get_course(course_id)
    if not existing:
        return jsonify({'message': 'Course not found'}), 404
    data = request.get_json()
    if not data.get('course_name') or not data.get('description') or not data.get('status'):
        return jsonify({'message': 'Missing required fields: course_name, description, status'}), 400
    course = course_service.update_course(
        course_id=course_id,
        course_name=data['course_name'],
        description=data['description'],
        status=data['status'],
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        created_at=existing.created_at,
        updated_at=datetime.utcnow(),
    )
    return jsonify({
        'id': course.id,
        'course_name': course.course_name,
        'description': course.description,
        'status': course.status,
    }), 200


@bp.route('/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """
    Delete a course
    ---
    delete:
      summary: Delete a course by ID
      parameters:
        - name: course_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Courses
      responses:
        204:
          description: Deleted
        404:
          description: Not found
    """
    existing = course_service.get_course(course_id)
    if not existing:
        return jsonify({'message': 'Course not found'}), 404
    course_service.delete_course(course_id)
    return '', 204
