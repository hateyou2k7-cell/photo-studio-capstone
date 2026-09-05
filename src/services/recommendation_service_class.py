"""
RecommendationService - class-based version.
Content-based scoring: user profile from completed reservations,
match against candidate Spaces by art_style + space_type + price.
"""
import math
from datetime import datetime

COMPLETED_STATUSES = {'completed', 'checked_out', 'confirmed', 'pending'}
WEIGHTS = {'style': 0.45, 'type': 0.3, 'price': 0.25}


class RecommendationService:
    def __init__(self, reservation_service, space_service):
        self.reservation_service = reservation_service
        self.space_service = space_service

    def _build_user_profile(self, user_id):
        reservations = [
            r for r in self.reservation_service.list(user_id=user_id)
            if r.status in COMPLETED_STATUSES and r.space_id
        ]
        if not reservations:
            return None

        style_weights = {}
        type_weights = {}
        price_sum = 0.0
        total_weight = 0.0
        booked_space_ids = set()

        for r in reservations:
            space = self.space_service.get(r.space_id)
            if not space:
                continue
            weight = self._recency_weight(r.start_time)
            style = space.art_style or 'unknown'
            style_weights[style] = style_weights.get(style, 0) + weight
            stype = space.space_type if hasattr(space, 'space_type') else (space.type.value if hasattr(space.type, 'value') else str(space.type))
            type_weights[stype] = type_weights.get(stype, 0) + weight
            price_sum += float(space.base_price_per_hour or 0) * weight
            total_weight += weight
            booked_space_ids.add(space.id)

        if total_weight == 0:
            return None

        return {
            'style_weights': style_weights,
            'type_weights': type_weights,
            'avg_price': price_sum / total_weight,
            'max_style_weight': max(style_weights.values()),
            'max_type_weight': max(type_weights.values()),
            'booked_space_ids': booked_space_ids,
        }

    @staticmethod
    def _recency_weight(start_time, half_life_days=30):
        if not start_time:
            return 0.5
        from datetime import timezone
        now = datetime.utcnow()
        if start_time.tzinfo is not None:
            now = now.replace(tzinfo=timezone.utc)
        days_ago = max((now - start_time).days, 0)
        return math.pow(0.5, days_ago / half_life_days)

    def _score_space(self, profile, space):
        style = space.art_style or 'unknown'
        style_score = profile['style_weights'].get(style, 0) / profile['max_style_weight']
        stype = space.space_type if hasattr(space, 'space_type') else (space.type.value if hasattr(space.type, 'value') else str(space.type))
        type_score = profile['type_weights'].get(stype, 0) / profile['max_type_weight']

        price = float(space.base_price_per_hour or 0)
        avg_price = profile['avg_price'] or 1
        price_diff_ratio = abs(price - avg_price) / avg_price
        price_score = math.exp(-price_diff_ratio)

        score = (
            style_score * WEIGHTS['style']
            + type_score * WEIGHTS['type']
            + price_score * WEIGHTS['price']
        )

        breakdown = {'style': round(style_score, 3), 'type': round(type_score, 3), 'price': round(price_score, 3)}
        top_factor = max(breakdown, key=breakdown.get)
        reason = {
            'style': f'Phong cách "{style}" khớp với gu bạn hay chọn',
            'type': f'Bạn thường đặt loại không gian "{stype}" như thế này',
            'price': 'Mức giá gần với ngân sách bạn thường chi trả',
        }[top_factor]

        return round(score, 3), reason

    def recommend(self, user_id, limit=5):
        profile = self._build_user_profile(user_id)
        all_spaces = self.space_service.list()

        if not profile:
            ranked = sorted(all_spaces, key=lambda s: (s.status is True), reverse=True)[:limit]
            return [
                {'space': s, 'score': None, 'reason': 'Phổ biến trên nền tảng (chưa có đủ lịch sử để gợi ý cá nhân hoá)'}
                for s in ranked
            ]

        candidates = [s for s in all_spaces if s.id not in profile['booked_space_ids']]
        scored = [
            {'space': s, 'score': score, 'reason': reason}
            for s in candidates
            for score, reason in [self._score_space(profile, s)]
        ]
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored[:limit]
