from marshmallow import Schema, fields


class PostRequestSchema(Schema):
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    category = fields.Str(required=False, load_default='article')
    is_published = fields.Bool(required=False, load_default=True)


class PostResponseSchema(Schema):
    id = fields.Int(required=True)
    author_id = fields.Int(required=True)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    category = fields.Method('get_category')
    is_published = fields.Bool(required=True)
    view_count = fields.Int(required=True)
    created_at = fields.Raw(required=False, allow_none=True)
    updated_at = fields.Raw(required=False, allow_none=True)

    def get_category(self, obj):
        value = obj.category
        return value.value if hasattr(value, 'value') else value


class CommentRequestSchema(Schema):
    user_id = fields.Int(required=False, load_default=None)
    content = fields.Str(required=True)


class CommentResponseSchema(Schema):
    id = fields.Int(required=True)
    post_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    content = fields.Str(required=True)
    created_at = fields.Raw(required=False, allow_none=True)


class WorkshopRequestSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=False, allow_none=True)
    scheduled_at = fields.DateTime(required=True)
    location = fields.Str(required=False, allow_none=True)
    capacity = fields.Int(required=False, load_default=10)
    price = fields.Int(required=False, load_default=0)


class WorkshopResponseSchema(Schema):
    id = fields.Int(required=True)
    expert_id = fields.Int(required=True)
    title = fields.Str(required=True)
    description = fields.Str(required=False, allow_none=True)
    scheduled_at = fields.DateTime(required=False, allow_none=True)
    location = fields.Str(required=False, allow_none=True)
    capacity = fields.Int(required=True)
    price = fields.Int(required=True)
    status = fields.Method('get_status')

    def get_status(self, obj):
        value = obj.status
        return value.value if hasattr(value, 'value') else value


class WorkshopRegistrationRequestSchema(Schema):
    user_id = fields.Int(required=False, load_default=None)


class WorkshopRegistrationResponseSchema(Schema):
    id = fields.Int(required=True)
    workshop_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    status = fields.Str(required=True)
    registered_at = fields.Raw(required=False, allow_none=True)
