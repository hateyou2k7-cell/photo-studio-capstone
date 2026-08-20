from marshmallow import Schema, fields

class SpaceImageResponseSchema(Schema):
    id = fields.Int(required=True)
    space_id = fields.Int(required=True)
    url = fields.Str(required=True)
    is_primary = fields.Bool(required=True)
    sort_order = fields.Int(required=True)
    created_at = fields.Raw(required=False, allow_none=True)

class SpaceImagePrimaryRequestSchema(Schema):
    is_primary = fields.Bool(required=True)