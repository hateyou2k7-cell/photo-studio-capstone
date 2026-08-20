from marshmallow import Schema, fields, validate

ROOM_TYPES = ['standard', 'vip', 'studio', 'conference']
ROOM_STATUSES = ['available', 'booked', 'maintenance']


class RoomRequestSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, error='name must not be empty'))
    description = fields.Str(required=False, allow_none=True)
    room_type = fields.Str(required=True, validate=validate.OneOf(ROOM_TYPES))
    capacity = fields.Int(required=True, validate=validate.Range(min=1, error='capacity must be >= 1'))
    price_per_hour = fields.Float(required=True, validate=validate.Range(min=0, error='price_per_hour must be >= 0'))
    status = fields.Str(required=True, validate=validate.OneOf(ROOM_STATUSES))


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