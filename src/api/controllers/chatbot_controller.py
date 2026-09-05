from flask import Blueprint, request, jsonify
from services.ai_assistant_service import AIAssistantService
from services.equipment_service import EquipmentService
from services.space_service import SpaceService
from services.reservation_service import ReservationService
from database.repositories.equipment_repository import EquipmentRepository
from database.repositories.space_repository import SpaceRepository
from database.repositories.reservation_repository import ReservationRepository
from services.recommendation_service_class import RecommendationService

bp = Blueprint('chatbot', __name__, url_prefix='/api/v1/chatbot')

_space_service = SpaceService(SpaceRepository())
_reservation_service = ReservationService(ReservationRepository())
_recommendation_service = RecommendationService(_reservation_service, _space_service)
ai_service = AIAssistantService(
    equipment_service=EquipmentService(EquipmentRepository()),
    space_service=_space_service,
    recommendation_service=_recommendation_service,
)


@bp.route('/ask', methods=['POST'])
def chat():
    """
    Ask the AI chatbot
    ---
    post:
      summary: Ask the AI photography assistant
      tags: [Chatbot]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: User message
                user_id:
                  type: integer
                  description: User ID for personalized responses
      responses:
        200:
          description: Chatbot response
        400:
          description: Invalid input
    """
    data = request.get_json()
    if not data or not data.get('message'):
        return jsonify({'message': 'message is required'}), 400
    try:
        result = ai_service.ask(
            message=data['message'],
            user_id=data.get('user_id'),
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(result), 200


@bp.route('/health', methods=['GET'])
def health():
    """
    Chatbot health check
    ---
    get:
      summary: Check chatbot service health
      tags: [Chatbot]
      responses:
        200:
          description: Health status
    """
    import os
    has_key = bool(os.environ.get('OPENAI_API_KEY'))
    return jsonify({
        'status': 'ok',
        'openai_configured': has_key,
        'mode': 'ai' if has_key else 'fallback',
    }), 200
