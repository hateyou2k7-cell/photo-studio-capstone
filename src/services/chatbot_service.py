import os
import re
import json
from openai import OpenAI

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get('OPENAI_API_KEY')
        if api_key:
            _client = OpenAI(api_key=api_key)
    return _client


FAQ_DATA = [
    {"keywords": ["35mm", "phim 35mm", "film 35mm"], "answer": "Phim 35mm là khổ phim phổ biến nhất, khổ 36x24mm, mỗi roll chụp được 24-36 ảnh. Phù hợp cho cả người mới bắt đầu."},
    {"keywords": ["120", "medium format", "phim 120"], "answer": "Phim 120 (medium format) cho chất lượng ảnh cao hơn 35mm, khổ 6x6, 6x7, 6x9. Phù hợp cho chụp chân dung và phong cảnh."},
    {"keywords": ["tráng phim", "developing", "hoá chất"], "answer": "Hoá chất tráng phim đen trắng cơ bản: Developer (D-76, Rodinal), Stop Bath, Fixer, Photo-Flo. Nhiệt độ và thời gian tuỳ loại phim."},
    {"keywords": ["rọi ảnh", "enlarger", "phóng to"], "answer": "Máy rọi (enlarger) dùng để phóng to phim ra giấy ảnh. Popular brands: Durst, Kaiser, Omega. CầnAdjustable head cho đa dạng kích thước."},
    {"keywords": ["quét phim", "scan", "scanner"], "answer": "Máy quét phim (film scanner) chuyển phim thành ảnh số. Flatbed scanner (Epson V600) quét được nhiều khổ, dedicated film scanner cho chất lượng cao hơn."},
    {"keywords": ["studio", "ánh sáng", "lighting"], "answer": "Ánh sáng studio gồm: key light, fill light, background light. Softbox cho ánh sáng mềm, reflector để lấp bóng."},
    {"keywords": ["C41", "c-41"], "answer": "C-41 là quy trình tráng phim màu phổ biến nhất. Có thể tráng tại nhà với bộ kit C-41 hoặc ra lab."},
    {"keywords": ["E6", "e-6", "slide", "positive"], "answer": "E-6 là quy trình tráng phim positive (slide/transparency). Đòi hỏi chính xác cao về nhiệt độ và thời gian."},
    {"keywords": ["push", "pull", "ISO"], "answer": "Push film = chụp ở ISO cao hơn ISO gốc rồi tráng bù. Pull = ngược lại. Push tăng contrast và grain, pull giảm contrast."},
]


def search_faq(query: str) -> dict:
    query_lower = query.lower()
    for entry in FAQ_DATA:
        for kw in entry['keywords']:
            if kw in query_lower:
                return {'answer': entry['answer']}
    return {'answer': 'Xin lỗi, tôi chưa tìm thấy thông tin phù hợp. Bạn có thể hỏi lại rõ hơn không?'}


def suggest_equipment_local(equipment_type: str = None, compatibility: str = None) -> dict:
    try:
        from infrastructure.databases.factory_database import FactoryDatabase
        from infrastructure.models.equipment_model import Equipment as EqModel, EquipmentType
        session = FactoryDatabase.get_database('POSTGREE').session
        query = session.query(EqModel).filter_by(is_available=True)
        if equipment_type:
            query = query.filter(EqModel.type == EquipmentType(equipment_type))
        items = query.all()
        if compatibility:
            items = [i for i in items if compatibility.lower() in (i.compatibility or '').lower()]
        return {
            'count': len(items),
            'items': [{'id': i.id, 'name': i.name, 'type': i.type.value if hasattr(i.type, 'value') else i.type,
                       'price_per_hour': float(i.price_per_hour or 0), 'compatibility': i.compatibility} for i in items],
        }
    except Exception as e:
        return {'count': 0, 'items': [], 'error': str(e)}


def suggest_rooms_local(space_type: str = None, art_style: str = None,
                        district: str = None, max_price: float = None) -> dict:
    try:
        from infrastructure.databases.factory_database import FactoryDatabase
        from infrastructure.models.film_space_model import Space, SpaceType
        session = FactoryDatabase.get_database('POSTGREE').session
        query = session.query(Space).filter_by(status=True)
        if space_type:
            query = query.filter(Space.type == SpaceType(space_type))
        items = query.all()
        if art_style:
            items = [i for i in items if art_style.lower() in (i.art_style or '').lower()]
        if district:
            items = [i for i in items if district.lower() in (i.address or '').lower()]
        if max_price is not None:
            items = [i for i in items if float(i.base_price_per_hour or 0) <= max_price]
        return {
            'count': len(items),
            'items': [{'id': i.id, 'name': i.name,
                       'type': i.type.value if hasattr(i.type, 'value') else i.type,
                       'address': i.address, 'art_style': i.art_style,
                       'price_per_hour': float(i.base_price_per_hour or 0)} for i in items],
        }
    except Exception as e:
        return {'count': 0, 'items': [], 'error': str(e)}


def suggest_packages_local(keyword: str = None, max_price: float = None) -> dict:
    try:
        from infrastructure.databases.factory_database import FactoryDatabase
        from infrastructure.models.film_package_model import ServicePackage
        session = FactoryDatabase.get_database('POSTGREE').session
        query = session.query(ServicePackage).filter_by(status=True)
        items = query.all()
        if keyword:
            items = [i for i in items if keyword.lower() in (i.name or '').lower() or keyword.lower() in (i.description or '').lower()]
        if max_price is not None:
            items = [i for i in items if float(i.price or 0) <= max_price]
        return {
            'count': len(items),
            'items': [{'id': i.id, 'name': i.name, 'price': float(i.price or 0), 'description': i.description} for i in items],
        }
    except Exception as e:
        return {'count': 0, 'items': [], 'error': str(e)}


AVAILABLE_FUNCTIONS = {
    'search_photography_faq': lambda **kw: search_faq(kw.get('query', '')),
    'suggest_equipment': lambda **kw: suggest_equipment_local(kw.get('type'), kw.get('compatibility')),
    'suggest_rooms': lambda **kw: suggest_rooms_local(kw.get('spaceType'), kw.get('artisticStyle'),
                                                      kw.get('district'), kw.get('maxPrice')),
    'suggest_packages': lambda **kw: suggest_packages_local(kw.get('keyword'), kw.get('maxPrice')),
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_photography_faq",
            "description": "Tra cứu kiến thức nhiếp ảnh phim (kỹ thuật, hoá chất, máy móc...).",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "Câu hỏi hoặc từ khoá"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_equipment",
            "description": "Gợi ý thiết bị nhiếp ảnh đang có trên hệ thống.",
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["camera", "enlarger", "scanner", "lighting", "tripod", "tank", "other"]},
                    "compatibility": {"type": "string", "description": "Khổ phim tương thích, vd '35mm'"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_rooms",
            "description": "Tìm phòng tối/studio trên hệ thống theo loại, phong cách, khu vực, giá.",
            "parameters": {
                "type": "object",
                "properties": {
                    "spaceType": {"type": "string", "enum": ["darkroom", "studio"]},
                    "artisticStyle": {"type": "string", "description": "Phong cách: vintage, minimalist, natural_light..."},
                    "district": {"type": "string", "description": "Khu vực/quận"},
                    "maxPrice": {"type": "number", "description": "Giá tối đa/giờ (VNĐ)"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_packages",
            "description": "Tìm gói dịch vụ trên hệ thống.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "Từ khoá tên gói"},
                    "maxPrice": {"type": "number", "description": "Giá tối đa (VNĐ)"},
                },
                "required": [],
            },
        },
    },
]

SYSTEM_PROMPT = """Bạn là trợ lý AI của nền tảng kết nối cộng đồng nhiếp ảnh phim.
Nhiệm vụ của bạn:
1. Trả lời câu hỏi về nhiếp ảnh phim (phim, hoá chất, kỹ thuật, máy móc...).
2. Khi người dùng muốn TÌM PHÒNG/STUDIO, dùng function suggest_rooms.
3. Khi người dùng muốn TÌM THIẾT BỊ, dùng function suggest_equipment.
4. Khi người dùng muốn TÌM GÓI DỊCH VỤ, dùng function suggest_packages.
Không tự bịa thông tin. Trả lời ngắn gọn, thân thiện, bằng tiếng Việt."""


def _fallback_reply(message: str) -> dict:
    msg = message.lower()
    if any(kw in msg for kw in ['phòng', 'studio', 'darkroom', 'tìm phòng', 'cho thuê phòng']):
        result = suggest_rooms_local()
        if result['items']:
            lines = [f"- {r['name']} ({r['type']}) - {r['price_per_hour']}/giờ" for r in result['items'][:5]]
            return {'answer': f"Tôi tìm thấy {result['count']} phòng:\n" + "\n".join(lines), 'used_function_call': True}
        return {'answer': 'Hiện tại chưa có phòng phù hợp.', 'used_function_call': True}
    if any(kw in msg for kw in ['thiết bị', 'máy', 'equipment', 'enlarger', 'scanner']):
        result = suggest_equipment_local()
        if result['items']:
            lines = [f"- {r['name']} ({r['type']}) - {r['price_per_hour']}/giờ" for r in result['items'][:5]]
            return {'answer': f"Tôi tìm thấy {result['count']} thiết bị:\n" + "\n".join(lines), 'used_function_call': True}
        return {'answer': 'Hiện tại chưa có thiết bị phù hợp.', 'used_function_call': True}
    if any(kw in msg for kw in ['gói', 'package', 'dịch vụ', 'combo']):
        result = suggest_packages_local()
        if result['items']:
            lines = [f"- {r['name']} - {r['price']}đ" for r in result['items'][:5]]
            return {'answer': f"Tôi tìm thấy {result['count']} gói dịch vụ:\n" + "\n".join(lines), 'used_function_call': True}
        return {'answer': 'Hiện tại chưa có gói dịch vụ phù hợp.', 'used_function_call': True}
    faq_result = search_faq(message)
    return {'answer': faq_result['answer'], 'used_function_call': False}


def ask_chatbot(message: str, history: list = None, user_id=None) -> dict:
    if not message or not message.strip():
        return {'answer': 'Vui lòng nhập câu hỏi.', 'used_function_call': False}

    client = _get_client()
    if not client:
        return _fallback_reply(message)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        reply = response.choices[0].message

        if reply.tool_calls:
            messages.append(reply)
            for tool_call in reply.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                func = AVAILABLE_FUNCTIONS.get(func_name)
                if func:
                    result = func(**func_args)
                else:
                    result = {"error": f"Function {func_name} not found"}
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                })
            second = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
            final_text = second.choices[0].message.content
        else:
            final_text = reply.content

        return {"answer": final_text, "used_function_call": bool(reply.tool_calls)}
    except Exception as e:
        return _fallback_reply(message)
