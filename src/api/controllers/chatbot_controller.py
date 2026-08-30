from flask import Blueprint, request, jsonify
from services.chatbot_service import ask_chatbot

bp = Blueprint('chatbot', __name__, url_prefix='/api/v1/chatbot')


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
                history:
                  type: array
                  description: Previous messages for context
                userId:
                  type: string
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
    result = ask_chatbot(
        message=data['message'],
        history=data.get('history'),
        user_id=data.get('userId'),
    )
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
