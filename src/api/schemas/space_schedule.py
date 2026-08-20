from marshmallow import Schema, fields

class SpaceScheduleRequestSchema(Schema):
    day_of_week = fields.Int(required=True)
    start_time = fields.Str(required=True)
    end_time = fields.Str(required=True)
    is_available = fields.Bool(required=False)

class SpaceScheduleResponseSchema(Schema):
    id = fields.Int(required=True)
    space_id = fields.Int(required=True)
    day_of_week = fields.Int(required=True)
    start_time = fields.Time(required=True)
    end_time = fields.Time(required=True)
    is_available = fields.Bool(required=True)
    created_at = fields.Raw(required=False, allow_none=True)
    updated_at = fields.Raw(required=False, allow_none=True)