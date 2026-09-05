"""
AI Assistant — Function-calling style chatbot.
Uses real data from system services (SpaceService, EquipmentService,
ServicePackage, RecommendationService) to answer photography questions.
Fallback mode: regex intent detection + FAQ. OpenAI mode: function calling.
"""
import os
import re

FAQ = [
    (
        {'35mm', 'máy rọi', 'enlarger'},
        'Phim 35mm thường dùng máy rọi (enlarger) đầu đèn condenser hoặc diffuser cỡ nhỏ, '
        'ví dụ Beseler 23C. Với 35mm bạn không cần đầu rọi khổ lớn dùng cho phim 120.',
    ),
    (
        {'120', 'medium format', 'trung'},
        'Phim 120 (medium format) cần máy rọi có đầu đèn hỗ trợ khổ 6x6/6x7 và ống kính rọi '
        'tiêu cự dài hơn (thường 80mm) so với 35mm (thường 50mm).',
    ),
    (
        {'tráng phim', 'hoá chất', 'developer', 'd-76'},
        'Quy trình tráng phim đen trắng cơ bản: Developer -> Stop bath -> Fixer -> rửa nước. '
        'Thời gian phụ thuộc độ pha loãng và nhiệt độ hoá chất.',
    ),
    (
        {'quét', 'scan', 'scanner'},
        'Với phim 35mm, máy quét như Plustek OpticFilm cho chất lượng tốt ở phân khúc phổ thông. '
        'Với khổ lớn hơn nên dùng scanner phẳng có khay film holder chuyên dụng.',
    ),
]

FAQ_FALLBACK = (
    'Mình chưa có dữ liệu chính xác cho câu hỏi này. Bạn có thể đăng câu hỏi lên mục '
    'Cộng đồng để các Photography Expert hỗ trợ, hoặc cho mình biết cụ thể hơn bạn cần '
    'tìm phòng, thiết bị hay gói dịch vụ nào nhé.'
)

CONDITION_LABEL = {'good': 'tình trạng tốt', 'needs_maintenance': 'đang bảo trì nhẹ', 'broken': 'đang hỏng'}


def _money(n):
    return f'{n:,.0f}đ'.replace(',', '.')


class AIAssistantService:
    def __init__(self, equipment_service=None, space_service=None,
                 package_service=None, recommendation_service=None):
        self.equipment_service = equipment_service
        self.space_service = space_service
        self.package_service = package_service
        self.recommendation_service = recommendation_service

    # ---- Functions (tools) ----

    def search_photography_faq(self, query: str) -> dict:
        q = query.lower()
        for keywords, answer in FAQ:
            if any(k in q for k in keywords):
                return {'answer': answer}
        return {'answer': FAQ_FALLBACK}

    def suggest_equipment(self, category=None, max_price=None) -> dict:
        try:
            items = self.equipment_service.list(filters={'available': True} if True else {})
            if category:
                items = [e for e in items if (e.equipment_type if hasattr(e, 'equipment_type') else (e.type.value if hasattr(e.type, 'value') else e.type)) == category]
            if max_price is not None:
                items = [e for e in items if float(e.price_per_hour or 0) <= max_price]
            return {
                'count': len(items),
                'items': [
                    {
                        'id': e.id, 'name': e.name,
                        'category': e.equipment_type if hasattr(e, 'equipment_type') else (e.type.value if hasattr(e.type, 'value') else e.type),
                        'price': float(e.price_per_hour or 0),
                        'condition': e.condition,
                        'description': getattr(e, 'description', None),
                    }
                    for e in items
                ],
            }
        except Exception as e:
            return {'count': 0, 'items': [], 'error': str(e)}

    def suggest_rooms(self, space_type=None, max_price=None) -> dict:
        try:
            filters = {}
            if space_type:
                filters['space_type'] = space_type
            if max_price is not None:
                filters['max_price'] = max_price
            items = self.space_service.search(filters) if filters else self.space_service.list()
            return {
                'count': len(items),
                'items': [
                    {
                        'id': s.id, 'name': s.name,
                        'price': float(s.base_price_per_hour or 0),
                        'art_style': getattr(s, 'art_style', None),
                        'description': getattr(s, 'description', None),
                        'max_capacity': getattr(s, 'max_capacity', None),
                        'amenities': getattr(s, 'amenities', None),
                    }
                    for s in items
                ],
            }
        except Exception as e:
            return {'count': 0, 'items': [], 'error': str(e)}

    def suggest_packages(self, max_price=None) -> dict:
        try:
            from database.databases.factory_database import FactoryDatabase
            from database.models.film_package_model import ServicePackage
            session = FactoryDatabase.get_database('POSTGREE').session
            query = session.query(ServicePackage).filter_by(status=True)
            rows = query.all()
            if max_price is not None:
                rows = [p for p in rows if float(p.price or 0) <= max_price]
            return {
                'count': len(rows),
                'items': [
                    {'id': p.id, 'name': p.name, 'price': float(p.price or 0), 'description': p.description}
                    for p in rows
                ],
            }
        except Exception as e:
            return {'count': 0, 'items': [], 'error': str(e)}

    def get_personalized_recommendations(self, user_id) -> dict:
        if not user_id:
            return {'error': 'missing_user_id'}
        results = self.recommendation_service.recommend(user_id, limit=3)
        return {
            'items': [
                {'id': r['space'].id, 'name': r['space'].name, 'reason': r['reason']}
                for r in results
            ]
        }

    # ---- Orchestration ----

    def ask(self, message: str, user_id=None) -> dict:
        if not message or not message.strip():
            raise ValueError('message không được để trống')
        if os.environ.get('OPENAI_API_KEY'):
            return self._ai_reply(message, user_id)
        return self._fallback_reply(message, user_id)

    # -- Regex intent detection --
    _RE_INTENT_VERB = re.compile(
        r'(gợi ý|thuê|đang có|có sẵn|tìm|bán|mua|tư vấn|báo giá|giá bao nhiêu|'
        r'còn (phòng|thiết bị|gói)|cho (mình|tôi) hỏi|bên (mình|bạn) có|cần thuê|muốn thuê|check giúp|'
        r'có (thiết bị|phòng|gói|máy|dịch vụ)|muốn (thuê|mua|tìm)|cần (thuê|mua|tìm))'
    )
    _RE_PERSONALIZED = re.compile(r'(dựa trên lịch sử|lịch sử đặt|phù hợp với tôi|gu của tôi)')
    _RE_ROOM = re.compile(r'(phòng|studio|darkroom|không gian)')
    _RE_PACKAGE = re.compile(r'(gói dịch vụ|gói combo|package|combo)')
    _RE_EQUIPMENT = re.compile(r'(thiết bị|máy (rọi|quét|ảnh)|đèn|ống kính|tripod|chân máy)')
    _RE_GENERIC_PRODUCT = re.compile(r'(sản phẩm|dịch vụ|bên (mình|bạn|shop)|shop|cửa hàng)')

    def _fallback_reply(self, message: str, user_id=None) -> dict:
        text = message.lower()
        has_intent_verb = bool(self._RE_INTENT_VERB.search(text))
        wants_personalized = bool(self._RE_PERSONALIZED.search(text))
        wants_room = bool(self._RE_ROOM.search(text))
        wants_package = bool(self._RE_PACKAGE.search(text))
        wants_equipment = bool(self._RE_EQUIPMENT.search(text))
        wants_generic_product = bool(self._RE_GENERIC_PRODUCT.search(text))

        if wants_personalized and wants_room:
            return self._reply_personalized(user_id)

        if wants_package and (has_intent_verb or wants_generic_product):
            return self._reply_packages()

        if wants_room and (has_intent_verb or wants_generic_product):
            return self._reply_rooms(text)

        if wants_equipment and (has_intent_verb or wants_generic_product):
            return self._reply_equipment(text)

        if wants_generic_product and has_intent_verb:
            return self._reply_overview()

        result = self.search_photography_faq(message)
        return {'answer': result['answer'], 'used_function': 'search_photography_faq'}

    # ---- Reply builders ----

    def _reply_personalized(self, user_id) -> dict:
        result = self.get_personalized_recommendations(user_id)
        if result.get('error'):
            return {
                'answer': 'Mình cần biết bạn là ai (chưa đăng nhập) để gợi ý phòng cá nhân hoá được.',
                'used_function': 'get_personalized_recommendations',
            }
        lines = [f"- {i['name']}: {i['reason']}" for i in result['items']]
        answer = "Dựa trên lịch sử đặt chỗ của bạn, mình gợi ý:\n" + "\n".join(lines)
        return {'answer': answer, 'used_function': 'get_personalized_recommendations'}

    def _reply_packages(self) -> dict:
        result = self.suggest_packages()
        if not result['count']:
            return {
                'answer': 'Hiện chưa có gói dịch vụ nào đang mở bán. Bạn cho mình biết nhu cầu cụ thể '
                         '(vd: chụp chân dung, tráng phim...) để mình gợi ý phòng/thiết bị lẻ phù hợp nhé.',
                'used_function': 'suggest_packages',
            }
        lines = []
        for p in result['items'][:5]:
            desc = f" — {p['description']}" if p.get('description') else ''
            lines.append(f"- {p['name']}: {_money(p['price'])}{desc}")
        answer = f"Hiện có {result['count']} gói dịch vụ đang mở bán:\n" + "\n".join(lines)
        answer += "\nBạn muốn xem chi tiết gói nào, mình gửi thêm thông tin?"
        return {'answer': answer, 'used_function': 'suggest_packages'}

    def _reply_rooms(self, text: str) -> dict:
        space_type = 'darkroom' if ('darkroom' in text or 'phòng tối' in text) else (
            'studio' if 'studio' in text else None)
        result = self.suggest_rooms(space_type=space_type)
        if not result['count']:
            return {
                'answer': 'Chưa tìm được phòng nào khớp yêu cầu, thử bỏ bớt tiêu chí (loại phòng, '
                         'khu vực, mức giá) hoặc cho mình biết bạn cần chụp gì để mình tư vấn thêm nhé.',
                'used_function': 'suggest_rooms',
            }
        lines = []
        for r in result['items'][:3]:
            style = f", phong cách {r['art_style']}" if r.get('art_style') else ''
            cap = f", sức chứa {r['max_capacity']} người" if r.get('max_capacity') else ''
            lines.append(f"- {r['name']}: {_money(r['price'])}/giờ{style}{cap}")
        answer = f"Mình tìm được {result['count']} phòng phù hợp, gợi ý top {min(3, result['count'])}:\n"
        answer += "\n".join(lines)
        answer += "\nBạn muốn xem lịch trống hay đặt luôn phòng nào không?"
        return {'answer': answer, 'used_function': 'suggest_rooms'}

    def _reply_equipment(self, text: str) -> dict:
        category = None
        if 'máy rọi' in text:
            category = 'enlarger'
        elif 'máy quét' in text or 'scan' in text:
            category = 'scanner'
        elif 'đèn' in text:
            category = 'lighting'
        elif 'máy ảnh' in text:
            category = 'camera'
        elif 'ống kính' in text:
            category = 'lens'
        elif 'chân máy' in text or 'tripod' in text:
            category = 'tripod'

        result = self.suggest_equipment(category=category)
        if not result['count']:
            return {
                'answer': 'Hiện chưa có thiết bị nào sẵn sàng khớp yêu cầu. Bạn cho mình biết loại '
                         'thiết bị và khổ phim (35mm/120) cụ thể để mình tìm chính xác hơn nhé.',
                'used_function': 'suggest_equipment',
            }
        lines = []
        for i in result['items'][:5]:
            cond = CONDITION_LABEL.get(i['condition'], i['condition'])
            lines.append(f"- {i['name']}: {_money(i['price'])}/giờ, {cond}")
        answer = f"Mình gợi ý {result['count']} thiết bị phù hợp:\n" + "\n".join(lines)
        answer += "\nBạn cần thêm thông tin khổ phim tương thích hay muốn thuê luôn?"
        return {'answer': answer, 'used_function': 'suggest_equipment'}

    def _reply_overview(self) -> dict:
        rooms = self.suggest_rooms()
        equipment = self.suggest_equipment()
        packages = self.suggest_packages()
        answer = (
            f"Bên mình hiện có {rooms['count']} phòng, {equipment['count']} thiết bị cho thuê "
            f"và {packages['count']} gói dịch vụ đang mở bán. Bạn đang cần tìm loại nào để mình "
            "tư vấn chi tiết hơn — phòng chụp/darkroom, thiết bị cụ thể, hay gói trọn gói?"
        )
        return {'answer': answer, 'used_function': 'overview'}

    def _ai_reply(self, message: str, user_id=None) -> dict:
        from openai import OpenAI
        client = OpenAI()
        tools = [
            {'type': 'function', 'function': {
                'name': 'search_photography_faq',
                'description': 'Tra cứu kiến thức nhiếp ảnh phim',
                'parameters': {'type': 'object', 'properties': {
                    'query': {'type': 'string'}}, 'required': ['query']},
            }},
            {'type': 'function', 'function': {
                'name': 'suggest_rooms',
                'description': 'Tìm phòng thật trên nền tảng',
                'parameters': {'type': 'object', 'properties': {
                    'space_type': {'type': 'string', 'enum': ['darkroom', 'studio']},
                    'max_price': {'type': 'number'}}},
            }},
            {'type': 'function', 'function': {
                'name': 'suggest_packages',
                'description': 'Tìm gói dịch vụ thật đang mở bán',
                'parameters': {'type': 'object', 'properties': {
                    'max_price': {'type': 'number'}}},
            }},
            {'type': 'function', 'function': {
                'name': 'suggest_equipment',
                'description': 'Tìm thiết bị thật đang sẵn có',
                'parameters': {'type': 'object', 'properties': {
                    'category': {'type': 'string'}, 'max_price': {'type': 'number'}}},
            }},
            {'type': 'function', 'function': {
                'name': 'get_personalized_recommendations',
                'description': 'Gợi ý phòng cá nhân hoá theo lịch sử đặt thật của user',
                'parameters': {'type': 'object', 'properties': {}},
            }},
        ]
        messages = [
            {'role': 'system', 'content':
                'Bạn là trợ lý CSKH của nền tảng nhiếp ảnh phim. Trả lời CHI TIẾT, đúng trọng tâm câu hỏi, '
                'liệt kê rõ tên/giá/đặc điểm khi có dữ liệu function trả về thay vì trả lời chung chung. '
                'Luôn dùng function khi câu hỏi cần dữ liệu thật (phòng/thiết bị/gói dịch vụ/gợi ý cá nhân).'},
            {'role': 'user', 'content': message},
        ]
        first = client.chat.completions.create(model=os.environ.get('OPENAI_MODEL', 'gpt-4o-mini'),
                                                messages=messages, tools=tools)
        choice = first.choices[0].message
        if not choice.tool_calls:
            return {'answer': choice.content, 'used_function': None}

        import json
        call = choice.tool_calls[0]
        args = json.loads(call.function.arguments or '{}')
        fn = getattr(self, call.function.name)
        if call.function.name == 'get_personalized_recommendations':
            result = fn(user_id)
        else:
            result = fn(**args)

        second = client.chat.completions.create(
            model=os.environ.get('OPENAI_MODEL', 'gpt-4o-mini'),
            messages=messages + [choice, {'role': 'tool', 'tool_call_id': call.id, 'content': json.dumps(result, ensure_ascii=False)}],
        )
        return {'answer': second.choices[0].message.content, 'used_function': call.function.name}
