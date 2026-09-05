from flask import Blueprint, request, jsonify
from services.recommendation_service import recommend

bp = Blueprint('recommendation', __name__, url_prefix='/api/v1/recommendations')


@bp.route('/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """
    Get personalized room recommendations for a user
    ---
    get:
      summary: Get personalized room recommendations based on booking history
      tags: [Recommendations]
      parameters:
        - name: user_id
          in: path
          required: true
          schema: {type: integer}
        - name: limit
          in: query
          schema: {type: integer, default: 3}
      responses:
        200:
          description: List of recommended rooms with scores
    """
    limit = int(request.args.get('limit', 3))
    results = recommend(user_id, limit=limit)
    return jsonify({
        'user_id': user_id,
        'count': len(results),
        'items': results,
    }), 200
