from marshmallow import Schema, fields

class RoomRequestSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(required=False, allow_none=True)
    room_type = fields.Str(required=False)
    capacity = fields.Int(required=False)
    price_per_hour = fields.Float(required=False)
    status = fields.Str(required=False)

class RoomResponseSchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True)
    description = fields.Str(required=False, allow_none=True)
    room_type = fields.Str(required=True)
    capacity = fields.Int(required=True)
    price_per_hour = fields.Float(required=True)
    status = fields.Str(required=True)
    created_at = fields.Raw(required=True)
    updated_at = fields.Raw(required=True)