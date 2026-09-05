from marshmallow import Schema, fields, validate


class EquipmentRequestSchema(Schema):
    provider_id = fields.Int(required=True)
    space_id = fields.Int(required=False, allow_none=True)
    name = fields.Str(required=True)
    model_name = fields.Str(required=False, allow_none=True)
    type = fields.Str(required=True, validate=validate.OneOf(['enlarger', 'camera', 'scanner', 'lighting', 'tripod', 'tank', 'other']))
    compatibility = fields.Str(required=False, allow_none=True)
    condition = fields.Str(required=False, load_default='good', validate=validate.OneOf(['excellent', 'good', 'fair', 'poor', 'broken']))
    description = fields.Str(required=False, allow_none=True)
    price_per_hour = fields.Float(required=False, load_default=0)
    is_available = fields.Bool(required=False, load_default=True)


class EquipmentUpdateSchema(Schema):
    space_id = fields.Int(required=False, allow_none=True)
    name = fields.Str(required=False)
    model_name = fields.Str(required=False, allow_none=True)
    type = fields.Str(required=False, validate=validate.OneOf(['enlarger', 'camera', 'scanner', 'lighting', 'tripod', 'tank', 'other']))
    compatibility = fields.Str(required=False, allow_none=True)
    condition = fields.Str(required=False, validate=validate.OneOf(['excellent', 'good', 'fair', 'poor', 'broken']))
    description = fields.Str(required=False, allow_none=True)
    price_per_hour = fields.Float(required=False)
    is_available = fields.Bool(required=False)


class EquipmentResponseSchema(Schema):
    id = fields.Int(required=True)
    provider_id = fields.Int(required=True)
    space_id = fields.Int(required=False, allow_none=True)
    name = fields.Str(required=True)
    model_name = fields.Str(required=False, allow_none=True)
    type = fields.Method('get_type')
    compatibility = fields.Str(required=False, allow_none=True)
    condition = fields.Method('get_condition')
    description = fields.Str(required=False, allow_none=True)
    price_per_hour = fields.Float(required=False)
    is_available = fields.Bool(required=True)
    created_at = fields.Raw(required=False, allow_none=True)
    updated_at = fields.Raw(required=False, allow_none=True)

    def get_type(self, obj):
        value = obj.type if hasattr(obj, 'type') else obj.equipment_type
        return value.value if hasattr(value, 'value') else value

    def get_condition(self, obj):
        value = obj.condition
        return value.value if hasattr(value, 'value') else value


class PackageBookingRequestSchema(Schema):
    package_id = fields.Int(required=True)
    space_id = fields.Int(required=True)
    customer_id = fields.Int(required=True)
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(required=True)
    notes = fields.Str(required=False, allow_none=True)


class PackageBookingResponseSchema(Schema):
    id = fields.Int(required=True)
    package_id = fields.Int(required=True)
    space_id = fields.Int(required=True)
    customer_id = fields.Int(required=True)
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(required=True)
    status = fields.Method('get_status')
    total_price = fields.Float(required=False)
    notes = fields.Str(required=False, allow_none=True)
    created_at = fields.Raw(required=False, allow_none=True)

    def get_status(self, obj):
        value = obj.status
        return value.value if hasattr(value, 'value') else value


class ResourceConflictSchema(Schema):
    resource_type = fields.Str()
    resource_id = fields.Int()
    resource_name = fields.Str()
    conflicting_start = fields.DateTime()
    conflicting_end = fields.DateTime()
