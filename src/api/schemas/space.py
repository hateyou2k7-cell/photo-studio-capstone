from marshmallow import Schema, fields

class SpaceRequestSchema(Schema):
    provider_id = fields.Int(required=True)
    name = fields.Str(required=True)
    space_type = fields.Str(required=True)
    description = fields.Str(required=False, allow_none=True)
    address = fields.Str(required=False, allow_none=True)
    max_capacity = fields.Int(required=False, allow_none=True)
    base_price_per_hour = fields.Float(required=False)
    status = fields.Bool(required=False)

class SpaceResponseSchema(Schema):
    id = fields.Int(required=True)
    provider_id = fields.Int(required=True)
    name = fields.Str(required=True)
    type = fields.Method('get_type')
    description = fields.Str(required=False, allow_none=True)
    address = fields.Str(required=False, allow_none=True)
    max_capacity = fields.Int(required=False, allow_none=True)
    base_price_per_hour = fields.Float(required=True)
    status = fields.Bool(required=True)
    created_at = fields.Raw(required=False, allow_none=True)
    updated_at = fields.Raw(required=False, allow_none=True)

    def get_type(self, obj):
        value = obj.type
        return value.value if hasattr(value, 'value') else value