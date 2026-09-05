from marshmallow import Schema, fields


class ProviderRequestSchema(Schema):
    user_id = fields.Int(required=True)
    business_name = fields.Str(required=True)
    description = fields.Str(required=False, allow_none=True)
    address = fields.Str(required=False, allow_none=True)


class ProviderResponseSchema(Schema):
    id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    business_name = fields.Str(required=True)
    description = fields.Str(required=False, allow_none=True)
    address = fields.Str(required=False, allow_none=True)
    status = fields.Str(required=True)
    created_at = fields.Raw(required=False, allow_none=True)
