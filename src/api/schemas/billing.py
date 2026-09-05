from marshmallow import Schema, fields


class InvoiceRequestSchema(Schema):
    customer_id = fields.Int(required=False)
    total_amount = fields.Float(required=False, load_default=0)
    status = fields.Str(required=False, load_default='pending')
    invoice_date = fields.DateTime(required=False, allow_none=True)
    blank_amount = fields.Float(required=False, load_default=0)
    paid_amount = fields.Float(required=False, load_default=0)


class InvoiceResponseSchema(Schema):
    id = fields.Int(required=True)
    customer_id = fields.Int(required=True)
    invoice_date = fields.Raw(required=False, allow_none=True)
    total_amount = fields.Float(required=True)
    status = fields.Str(required=True)
    invoice_code = fields.Str(required=False, allow_none=True)
    created_at = fields.Raw(required=False, allow_none=True)
    updated_at = fields.Raw(required=False, allow_none=True)
    blank_amount = fields.Float(required=False)
    paid_amount = fields.Float(required=False)


class InvoiceItemRequestSchema(Schema):
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=False, load_default=1)
    unit_price = fields.Float(required=False, load_default=0)


class InvoiceItemResponseSchema(Schema):
    id = fields.Int(required=True)
    invoice_id = fields.Int(required=True)
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True)
    unit_price = fields.Float(required=True)
    total_price = fields.Float(required=True)
    created_at = fields.Raw(required=False, allow_none=True)
    updated_at = fields.Raw(required=False, allow_none=True)


class CustomerRequestSchema(Schema):
    customer_name = fields.Str(required=True)
    email = fields.Email(required=False, allow_none=True)
    phone = fields.Str(required=False, allow_none=True)
    address = fields.Str(required=False, allow_none=True)


class CustomerResponseSchema(Schema):
    id = fields.Int(required=True)
    customer_name = fields.Str(required=True)
    email = fields.Email(required=False, allow_none=True)
    phone = fields.Str(required=False, allow_none=True)
    address = fields.Str(required=False, allow_none=True)
    created_at = fields.Raw(required=False, allow_none=True)
    updated_at = fields.Raw(required=False, allow_none=True)


class ProductRequestSchema(Schema):
    product_name = fields.Str(required=True)
    description = fields.Str(required=False, allow_none=True)
    product_code = fields.Str(required=False, allow_none=True)


class ProductResponseSchema(Schema):
    id = fields.Int(required=True)
    product_name = fields.Str(required=True)
    description = fields.Str(required=False, allow_none=True)
    product_code = fields.Str(required=False, allow_none=True)
    created_at = fields.Raw(required=False, allow_none=True)
    updated_at = fields.Raw(required=False, allow_none=True)


class PayTransactionRequestSchema(Schema):
    amount = fields.Float(required=True)
    payment_method = fields.Str(required=True)


class PayTransactionResponseSchema(Schema):
    id = fields.Int(required=True)
    invoice_id = fields.Int(required=True)
    amount = fields.Float(required=True)
    payment_method = fields.Str(required=True)
    transaction_date = fields.Raw(required=False, allow_none=True)
