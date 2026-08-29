from typing import List, Optional
from datetime import datetime
from domain.models.billing import Invoice, InvoiceItem, Customer, Product, PayTransaction
from domain.models.ibilling_repository import IInvoiceRepository

INVOICE_STATUSES = {'pending', 'paid', 'partial', 'cancelled', 'refunded'}
PAYMENT_METHODS = {'cash', 'bank_transfer', 'vnpay', 'momo'}


class BillingService:
    def __init__(self, repository: IInvoiceRepository):
        self.repository = repository

    def create_invoice(self, customer_id: int, total_amount=0, status='pending',
                       invoice_date=None) -> Invoice:
        invoice = Invoice(
            id=None, customer_id=customer_id,
            invoice_date=invoice_date or datetime.utcnow(),
            total_amount=total_amount, status=status,
        )
        return self.repository.add(invoice)

    def get_invoice(self, invoice_id: int) -> Optional[Invoice]:
        return self.repository.get_by_id(invoice_id)

    def list_invoices(self, customer_id=None, status=None) -> List[Invoice]:
        if status and status not in INVOICE_STATUSES:
            raise ValueError(f'status must be one of {INVOICE_STATUSES}')
        return self.repository.list(customer_id=customer_id, status=status)

    def update_invoice(self, invoice_id: int, customer_id: int, total_amount=0,
                       status='pending', invoice_date=None, blank_amount=0,
                       paid_amount=0) -> Invoice:
        existing = self.repository.get_by_id(invoice_id)
        if not existing:
            raise ValueError('Invoice not found')
        invoice = Invoice(
            id=invoice_id, customer_id=customer_id,
            invoice_date=invoice_date or existing.invoice_date,
            total_amount=total_amount, status=status,
            blank_amount=blank_amount, paid_amount=paid_amount,
        )
        return self.repository.update(invoice)

    def delete_invoice(self, invoice_id: int) -> None:
        existing = self.repository.get_by_id(invoice_id)
        if not existing:
            raise ValueError('Invoice not found')
        self.repository.delete(invoice_id)

    def add_item(self, invoice_id: int, product_id: int, quantity=1,
                 unit_price=0) -> InvoiceItem:
        existing = self.repository.get_by_id(invoice_id)
        if not existing:
            raise ValueError('Invoice not found')
        total_price = quantity * unit_price
        item = InvoiceItem(
            id=None, invoice_id=invoice_id, product_id=product_id,
            quantity=quantity, unit_price=unit_price, total_price=total_price,
        )
        saved = self.repository.add_item(item)
        self._recalculate_total(invoice_id)
        return saved

    def list_items(self, invoice_id: int) -> List[InvoiceItem]:
        return self.repository.list_items(invoice_id)

    def delete_item(self, item_id: int) -> None:
        self.repository.delete_item(item_id)

    def _recalculate_total(self, invoice_id: int):
        items = self.repository.list_items(invoice_id)
        total = sum(float(i.total_price or 0) for i in items)
        existing = self.repository.get_by_id(invoice_id)
        if existing:
            existing.total_amount = total
            self.repository.session.commit()

    def create_customer(self, customer_name: str, email: str = None,
                        phone: str = None, address: str = None) -> Customer:
        customer = Customer(
            id=None, customer_name=customer_name, email=email,
            phone=phone, address=address,
        )
        return self.repository.add_customer(customer)

    def get_customer(self, customer_id: int) -> Optional[Customer]:
        return self.repository.get_customer(customer_id)

    def list_customers(self) -> List[Customer]:
        return self.repository.list_customers()

    def update_customer(self, customer_id: int, customer_name: str, email: str = None,
                        phone: str = None, address: str = None) -> Customer:
        existing = self.repository.get_customer(customer_id)
        if not existing:
            raise ValueError('Customer not found')
        customer = Customer(
            id=customer_id, customer_name=customer_name, email=email,
            phone=phone, address=address,
        )
        return self.repository.update_customer(customer)

    def delete_customer(self, customer_id: int) -> None:
        existing = self.repository.get_customer(customer_id)
        if not existing:
            raise ValueError('Customer not found')
        self.repository.delete_customer(customer_id)

    def create_product(self, product_name: str, description: str = None,
                       product_code: str = None) -> Product:
        product = Product(
            id=None, product_name=product_name, description=description,
            product_code=product_code,
        )
        return self.repository.add_product(product)

    def get_product(self, product_id: int) -> Optional[Product]:
        return self.repository.get_product(product_id)

    def list_products(self) -> List[Product]:
        return self.repository.list_products()

    def update_product(self, product_id: int, product_name: str, description: str = None,
                       product_code: str = None) -> Product:
        existing = self.repository.get_product(product_id)
        if not existing:
            raise ValueError('Product not found')
        product = Product(
            id=product_id, product_name=product_name, description=description,
            product_code=product_code,
        )
        return self.repository.update_product(product)

    def delete_product(self, product_id: int) -> None:
        existing = self.repository.get_product(product_id)
        if not existing:
            raise ValueError('Product not found')
        self.repository.delete_product(product_id)

    def add_payment(self, invoice_id: int, amount: float, payment_method: str = 'cash') -> PayTransaction:
        existing = self.repository.get_by_id(invoice_id)
        if not existing:
            raise ValueError('Invoice not found')
        if payment_method not in PAYMENT_METHODS:
            raise ValueError(f'payment_method must be one of {PAYMENT_METHODS}')
        payment = PayTransaction(
            id=None, invoice_id=invoice_id, amount=amount,
            payment_method=payment_method,
        )
        saved = self.repository.add_payment(payment)
        self._update_invoice_payment(invoice_id, amount)
        return saved

    def list_payments(self, invoice_id: int) -> List[PayTransaction]:
        return self.repository.list_payments(invoice_id)

    def _update_invoice_payment(self, invoice_id: int, amount: float):
        existing = self.repository.get_by_id(invoice_id)
        if existing:
            existing.paid_amount = float(existing.paid_amount or 0) + amount
            if existing.paid_amount >= float(existing.total_amount or 0):
                existing.status = 'paid'
            else:
                existing.status = 'partial'
            existing.updated_at = datetime.utcnow()
            self.repository.session.commit()
