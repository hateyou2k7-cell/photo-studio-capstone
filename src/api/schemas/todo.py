from marshmallow import Schema, fields


class TodoRequestSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=False, allow_none=True)
    status = fields.Str(required=True)


class TodoResponseSchema(Schema):
    id = fields.Int(required=True)
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    status = fields.Str(required=True)
    created_at = fields.Raw(allow_none=True)
    updated_at = fields.Raw(allow_none=True)
