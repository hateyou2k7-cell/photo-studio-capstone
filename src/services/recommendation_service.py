import math
from typing import List
from database.databases.factory_database import FactoryDatabase
from database.models.film_space_model import Space, SpaceType
from database.models.film_package_model import ServicePackage
from database.models.package_booking_model import PackageBooking, BookingStatus


def _haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(float(lat2) - float(lat1))
    dlon = math.radians(float(lon2) - float(lon1))
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(float(lat1))) * math.cos(math.radians(float(lat2))) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _build_user_profile(customer_id: int) -> dict:
    session = FactoryDatabase.get_database('POSTGREE').session
    bookings = session.query(PackageBooking).filter(
        PackageBooking.customer_id == customer_id,
        PackageBooking.status.in_(['confirmed', 'completed']),
    ).all()
    if not bookings:
        return {'has_history': False}
    style_weights = {}
    type_weights = {}
    prices = []
    booked_space_ids = set()
    recency_scores = []
    from datetime import datetime
    now = datetime.utcnow()
    for b in bookings:
        space = session.query(Space).filter_by(id=b.space_id).first()
        if not space:
            continue
        booked_space_ids.add(space.id)
        style = space.art_style or 'unknown'
        style_weights[style] = style_weights.get(style, 0) + 1
        stype = space.type.value if hasattr(space.type, 'value') else str(space.type)
        type_weights[stype] = type_weights.get(stype, 0) + 1
        prices.append(float(space.base_price_per_hour or 0))
        days_ago = (now - (b.created_at or now)).days
        recency = math.exp(-days_ago / 30.0)
        recency_scores.append(recency)
    total = sum(style_weights.values()) or 1
    style_weights = {k: v / total for k, v in style_weights.items()}
    total = sum(type_weights.values()) or 1
    type_weights = {k: v / total for k, v in type_weights.items()}
    return {
        'has_history': True,
        'style_weights': style_weights,
        'type_weights': type_weights,
        'avg_price': sum(prices) / len(prices) if prices else 0,
        'booked_space_ids': booked_space_ids,
        'avg_recency': sum(recency_scores) / len(recency_scores) if recency_scores else 0,
    }


def _score_room(space, profile: dict) -> dict:
    score = 0
    reasons = []
    if not profile.get('has_history'):
        score = float(space.base_price_per_hour or 0)
        return {'score': score, 'reason': 'Popular room (cold start)'}
    style = space.art_style or 'unknown'
    style_score = profile['style_weights'].get(style, 0)
    score += style_score * 0.35
    if style_score > 0:
        reasons.append(f"Phong cách '{style}' phù hợp")
    stype = space.type.value if hasattr(space.type, 'value') else str(space.type)
    type_score = profile['type_weights'].get(stype, 0)
    score += type_score * 0.25
    if type_score > 0:
        reasons.append(f"Loại '{stype}' phù hợp")
    room_price = float(space.base_price_per_hour or 0)
    avg_price = profile.get('avg_price', 0)
    if avg_price > 0:
        price_ratio = abs(room_price - avg_price) / avg_price
        price_score = math.exp(-price_ratio)
        score += price_score * 0.20
        if price_ratio < 0.3:
            reasons.append('Giá phù hợp')
    lat = float(space.latitude or 0)
    lng = float(space.longitude or 0)
    if lat and lng:
        loc_score = math.exp(-5.0 / 5.0)
        score += loc_score * 0.20
    if space.id in profile.get('booked_space_ids', set()):
        score *= 0.5
        reasons.append('Đã đặt trước đó')
    return {'score': round(score, 4), 'reason': '; '.join(reasons) if reasons else 'Phù hợp chung'}


def recommend(customer_id: int, limit: int = 3) -> list:
    session = FactoryDatabase.get_database('POSTGREE').session
    profile = _build_user_profile(customer_id)
    spaces = session.query(Space).filter_by(status=True).all()
    scored = []
    for space in spaces:
        result = _score_room(space, profile)
        scored.append({
            'space': {
                'id': space.id,
                'name': space.name,
                'type': space.type.value if hasattr(space.type, 'value') else str(space.type),
                'address': space.address,
                'art_style': space.art_style,
                'price_per_hour': float(space.base_price_per_hour or 0),
            },
            'score': result['score'],
            'reason': result['reason'],
        })
    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored[:limit]
