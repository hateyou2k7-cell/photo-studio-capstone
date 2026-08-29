import pytest
from services.billing_service import BillingService, INVOICE_STATUSES, PAYMENT_METHODS


class FakeBillingRepo:
    def __init__(self):
        self.invoices = []
        self.items = []
        self.customers = []
        self.products = []
        self.payments = []
        self._invoice_counter = 1
        self._item_counter = 1
        self._customer_counter = 1
        self._product_counter = 1
        self._payment_counter = 1

    def add(self, invoice):
        invoice.id = self._invoice_counter
        invoice.invoice_code = f'INV-{self._invoice_counter:04d}'
        self._invoice_counter += 1
        self.invoices.append(invoice)
        return invoice

    def get_by_id(self, invoice_id):
        return next((i for i in self.invoices if i.id == invoice_id), None)

    def list(self, customer_id=None, status=None):
        result = self.invoices
        if customer_id is not None:
            result = [i for i in result if i.customer_id == customer_id]
        if status is not None:
            result = [i for i in result if i.status == status]
        return result

    def update(self, invoice):
        for i, inv in enumerate(self.invoices):
            if inv.id == invoice.id:
                self.invoices[i] = invoice
                return invoice
        raise ValueError('Invoice not found')

    def delete(self, invoice_id):
        self.invoices = [i for i in self.invoices if i.id != invoice_id]

    def add_item(self, item):
        item.id = self._item_counter
        self._item_counter += 1
        self.items.append(item)
        return item

    def list_items(self, invoice_id):
        return [i for i in self.items if i.invoice_id == invoice_id]

    def delete_item(self, item_id):
        self.items = [i for i in self.items if i.id != item_id]

    def add_customer(self, customer):
        customer.id = self._customer_counter
        self._customer_counter += 1
        self.customers.append(customer)
        return customer

    def get_customer(self, customer_id):
        return next((c for c in self.customers if c.id == customer_id), None)

    def list_customers(self):
        return list(self.customers)

    def update_customer(self, customer):
        for i, c in enumerate(self.customers):
            if c.id == customer.id:
                self.customers[i] = customer
                return customer
        raise ValueError('Customer not found')

    def delete_customer(self, customer_id):
        self.customers = [c for c in self.customers if c.id != customer_id]

    def add_product(self, product):
        product.id = self._product_counter
        self._product_counter += 1
        self.products.append(product)
        return product

    def get_product(self, product_id):
        return next((p for p in self.products if p.id == product_id), None)

    def list_products(self):
        return list(self.products)

    def update_product(self, product):
        for i, p in enumerate(self.products):
            if p.id == product.id:
                self.products[i] = product
                return product
        raise ValueError('Product not found')

    def delete_product(self, product_id):
        self.products = [p for p in self.products if p.id != product_id]

    def add_payment(self, payment):
        payment.id = self._payment_counter
        self._payment_counter += 1
        self.payments.append(payment)
        return payment

    def list_payments(self, invoice_id):
        return [p for p in self.payments if p.invoice_id == invoice_id]


@pytest.fixture
def service():
    return BillingService(FakeBillingRepo())


def test_create_invoice(service):
    invoice = service.create_invoice(customer_id=1, total_amount=500)
    assert invoice.id == 1
    assert invoice.invoice_code == 'INV-0001'
    assert invoice.status == 'pending'


def test_get_invoice(service):
    service.create_invoice(customer_id=1, total_amount=500)
    result = service.get_invoice(1)
    assert result is not None


def test_get_invoice_not_found(service):
    assert service.get_invoice(999) is None


def test_list_invoices(service):
    service.create_invoice(customer_id=1, total_amount=100)
    service.create_invoice(customer_id=2, total_amount=200)
    assert len(service.list_invoices()) == 2


def test_list_invoices_by_customer(service):
    service.create_invoice(customer_id=1, total_amount=100)
    service.create_invoice(customer_id=2, total_amount=200)
    assert len(service.list_invoices(customer_id=1)) == 1


def test_list_invoices_invalid_status(service):
    with pytest.raises(ValueError):
        service.list_invoices(status='invalid')


def test_delete_invoice(service):
    service.create_invoice(customer_id=1, total_amount=100)
    service.delete_invoice(1)
    assert service.get_invoice(1) is None


def test_delete_invoice_not_found(service):
    with pytest.raises(ValueError):
        service.delete_invoice(999)


def test_add_item(service):
    service.create_invoice(customer_id=1, total_amount=0)
    item = service.add_item(1, product_id=1, quantity=2, unit_price=50)
    assert item.total_price == 100


def test_add_item_invoice_not_found(service):
    with pytest.raises(ValueError):
        service.add_item(999, product_id=1)


def test_list_items(service):
    service.create_invoice(customer_id=1, total_amount=0)
    service.add_item(1, product_id=1, quantity=1, unit_price=50)
    service.add_item(1, product_id=2, quantity=2, unit_price=30)
    assert len(service.list_items(1)) == 2


def test_create_customer(service):
    customer = service.create_customer(customer_name='John', email='john@test.com')
    assert customer.id == 1
    assert customer.customer_name == 'John'


def test_get_customer(service):
    service.create_customer(customer_name='John')
    result = service.get_customer(1)
    assert result is not None


def test_list_customers(service):
    service.create_customer(customer_name='John')
    service.create_customer(customer_name='Jane')
    assert len(service.list_customers()) == 2


def test_update_customer(service):
    service.create_customer(customer_name='John')
    result = service.update_customer(1, customer_name='John Updated', phone='123456')
    assert result.customer_name == 'John Updated'


def test_delete_customer(service):
    service.create_customer(customer_name='John')
    service.delete_customer(1)
    assert service.get_customer(1) is None


def test_create_product(service):
    product = service.create_product(product_name='Camera', product_code='CAM001')
    assert product.id == 1
    assert product.product_code == 'CAM001'


def test_list_products(service):
    service.create_product(product_name='Camera')
    service.create_product(product_name='Lens')
    assert len(service.list_products()) == 2


def test_add_payment(service):
    service.create_invoice(customer_id=1, total_amount=500)
    payment = service.add_payment(1, amount=200, payment_method='cash')
    assert payment.id == 1
    assert payment.amount == 200


def test_add_payment_invalid_method(service):
    service.create_invoice(customer_id=1, total_amount=500)
    with pytest.raises(ValueError):
        service.add_payment(1, amount=200, payment_method='bitcoin')


def test_add_payment_updates_invoice_status(service):
    service.create_invoice(customer_id=1, total_amount=500)
    service.add_payment(1, amount=500, payment_method='cash')
    invoice = service.get_invoice(1)
    assert invoice.status == 'paid'
    assert invoice.paid_amount == 500


def test_add_partial_payment(service):
    service.create_invoice(customer_id=1, total_amount=500)
    service.add_payment(1, amount=200, payment_method='cash')
    invoice = service.get_invoice(1)
    assert invoice.status == 'partial'
    assert invoice.paid_amount == 200


def test_invoice_statuses():
    assert 'pending' in INVOICE_STATUSES
    assert 'paid' in INVOICE_STATUSES


def test_payment_methods():
    assert 'cash' in PAYMENT_METHODS
    assert 'vnpay' in PAYMENT_METHODS
    assert 'momo' in PAYMENT_METHODS
