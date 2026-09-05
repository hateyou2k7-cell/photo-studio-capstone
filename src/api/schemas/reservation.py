from marshmallow import Schema, fields


class ReservationRequestSchema(Schema):
    user_id = fields.Int(required=True)
    provider_id = fields.Int(required=True)
    space_id = fields.Int(required=False, allow_none=True)
    package_id = fields.Int(required=False, allow_none=True)
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(required=True)
    total_price = fields.Float(required=False, load_default=0)
    status = fields.Str(required=False, load_default='pending')
    qr_code = fields.Str(required=False, allow_none=True)


class ReservationResponseSchema(Schema):
    id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    provider_id = fields.Int(required=True)
    space_id = fields.Int(required=False, allow_none=True)
    package_id = fields.Int(required=False, allow_none=True)
    start_time = fields.DateTime(required=False, allow_none=True)
    end_time = fields.DateTime(required=False, allow_none=True)
    total_price = fields.Float(required=True)
    status = fields.Method('get_status')
    qr_code = fields.Str(required=False, allow_none=True)
    created_at = fields.Raw(required=False, allow_none=True)
    updated_at = fields.Raw(required=False, allow_none=True)

    def get_status(self, obj):
        value = obj.status
        return value.value if hasattr(value, 'value') else value


class ReservationItemRequestSchema(Schema):
    item_type = fields.Str(required=True)
    item_id = fields.Int(required=True)
    quantity = fields.Int(required=False, load_default=1)
    price_at_booking = fields.Float(required=False, load_default=0)


class ReservationItemResponseSchema(Schema):
    id = fields.Int(required=True)
    reservation_id = fields.Int(required=True)
    item_type = fields.Method('get_item_type')
    item_id = fields.Int(required=True)
    quantity = fields.Int(required=True)
    price_at_booking = fields.Float(required=True)

    def get_item_type(self, obj):
        value = obj.item_type
        return value.value if hasattr(value, 'value') else value


class PaymentRequestSchema(Schema):
    user_id = fields.Int(required=True)
    amount = fields.Float(required=True)
    method = fields.Str(required=True)
    transaction_ref = fields.Str(required=False, allow_none=True)


class PaymentResponseSchema(Schema):
    id = fields.Int(required=True)
    reservation_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    amount = fields.Float(required=True)
    method = fields.Method('get_method')
    status = fields.Method('get_status')
    transaction_ref = fields.Str(required=False, allow_none=True)
    created_at = fields.Raw(required=False, allow_none=True)

    def get_method(self, obj):
        value = obj.method
        return value.value if hasattr(value, 'value') else value

    def get_status(self, obj):
        value = obj.status
        return value.value if hasattr(value, 'value') else value


class ServiceSessionResponseSchema(Schema):
    id = fields.Int(required=True)
    reservation_id = fields.Int(required=True)
    checked_in_at = fields.DateTime(required=False, allow_none=True)
    checked_out_at = fields.DateTime(required=False, allow_none=True)
    actual_duration_minutes = fields.Int(required=False, allow_none=True)
    status = fields.Method('get_status')

    def get_status(self, obj):
        value = obj.status
        return value.value if hasattr(value, 'value') else value


class ReviewRequestSchema(Schema):
    user_id = fields.Int(required=True)
    space_id = fields.Int(required=False, allow_none=True)
    rating = fields.Int(required=True)
    comment = fields.Str(required=False, allow_none=True)


class ReviewResponseSchema(Schema):
    id = fields.Int(required=True)
    reservation_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    space_id = fields.Int(required=False, allow_none=True)
    rating = fields.Int(required=True)
    comment = fields.Str(required=False, allow_none=True)
    created_at = fields.Raw(required=False, allow_none=True)
