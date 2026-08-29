class Invoice:
    def __init__(self, id, customer_id, invoice_date=None, total_amount=0,
                 status='pending', invoice_code=None, created_at=None, updated_at=None,
                 blank_amount=0, paid_amount=0):
        self.id = id
        self.customer_id = customer_id
        self.invoice_date = invoice_date
        self.total_amount = total_amount
        self.status = status
        self.invoice_code = invoice_code
        self.created_at = created_at
        self.updated_at = updated_at
        self.blank_amount = blank_amount
        self.paid_amount = paid_amount


class InvoiceItem:
    def __init__(self, id, invoice_id, product_id, quantity=1,
                 unit_price=0, total_price=0, created_at=None, updated_at=None):
        self.id = id
        self.invoice_id = invoice_id
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.total_price = total_price
        self.created_at = created_at
        self.updated_at = updated_at


class Customer:
    def __init__(self, id, customer_name=None, email=None, phone=None,
                 address=None, created_at=None, updated_at=None):
        self.id = id
        self.customer_name = customer_name
        self.email = email
        self.phone = phone
        self.address = address
        self.created_at = created_at
        self.updated_at = updated_at


class Product:
    def __init__(self, id, product_name=None, description=None,
                 product_code=None, created_at=None, updated_at=None):
        self.id = id
        self.product_name = product_name
        self.description = description
        self.product_code = product_code
        self.created_at = created_at
        self.updated_at = updated_at


class PayTransaction:
    def __init__(self, id, invoice_id, amount=0, payment_method='cash',
                 transaction_date=None):
        self.id = id
        self.invoice_id = invoice_id
        self.amount = amount
        self.payment_method = payment_method
        self.transaction_date = transaction_date
