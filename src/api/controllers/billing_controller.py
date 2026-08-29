from flask import Blueprint, request, jsonify
from api.auth_middleware import jwt_required
from api.pagination import paginate_list
from services.billing_service import BillingService
from infrastructure.repositories.billing_repository import InvoiceRepository
from api.schemas.billing import (
    InvoiceRequestSchema, InvoiceResponseSchema,
    InvoiceItemRequestSchema, InvoiceItemResponseSchema,
    CustomerRequestSchema, CustomerResponseSchema,
    ProductRequestSchema, ProductResponseSchema,
    PayTransactionRequestSchema, PayTransactionResponseSchema,
)

bp = Blueprint('billing', __name__, url_prefix='/v1/billing')

billing_service = BillingService(InvoiceRepository())
invoice_request = InvoiceRequestSchema()
invoice_response = InvoiceResponseSchema()
item_request = InvoiceItemRequestSchema()
item_response = InvoiceItemResponseSchema()
customer_request = CustomerRequestSchema()
customer_response = CustomerResponseSchema()
product_request = ProductRequestSchema()
product_response = ProductResponseSchema()
payment_request = PayTransactionRequestSchema()
payment_response = PayTransactionResponseSchema()


@bp.route('/invoices', methods=['GET'])
def list_invoices():
    """
    List invoices
    ---
    get:
      summary: List invoices with optional filters
      parameters:
        - name: customer_id
          in: query
          schema:
            type: integer
        - name: status
          in: query
          schema:
            type: string
            enum: [pending, paid, partial, cancelled, refunded]
      tags:
        - Billing
      responses:
        200:
          description: List of invoices
    """
    customer_id = request.args.get('customer_id', type=int)
    status = request.args.get('status')
    try:
        invoices = billing_service.list_invoices(customer_id=customer_id, status=status)
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(paginate_list(invoices, invoice_response)), 200


@bp.route('/invoices/<int:invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    """
    Get invoice by ID
    ---
    get:
      summary: Get an invoice by ID
      parameters:
        - name: invoice_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Billing
      responses:
        200:
          description: Invoice object
        404:
          description: Not found
    """
    invoice = billing_service.get_invoice(invoice_id)
    if not invoice:
        return jsonify({'message': 'Invoice not found'}), 404
    return jsonify(invoice_response.dump(invoice)), 200


@bp.route('/invoices', methods=['POST'])
@jwt_required
def create_invoice():
    """
    Create a new invoice
    ---
    post:
      summary: Create a new invoice
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/InvoiceRequest'
      tags:
        - Billing
      responses:
        201:
          description: Created
        400:
          description: Invalid input
    """
    data = request.get_json()
    errors = invoice_request.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        invoice = billing_service.create_invoice(
            customer_id=data['customer_id'],
            total_amount=data.get('total_amount', 0),
            status=data.get('status', 'pending'),
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(invoice_response.dump(invoice)), 201


@bp.route('/invoices/<int:invoice_id>', methods=['PUT'])
@jwt_required
def update_invoice(invoice_id):
    """
    Update an invoice
    ---
    put:
      summary: Update an invoice by ID
      parameters:
        - name: invoice_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/InvoiceRequest'
      tags:
        - Billing
      responses:
        200:
          description: Updated
        400:
          description: Invalid input
        404:
          description: Not found
    """
    existing = billing_service.get_invoice(invoice_id)
    if not existing:
        return jsonify({'message': 'Invoice not found'}), 404
    data = request.get_json()
    errors = invoice_request.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        invoice = billing_service.update_invoice(
            invoice_id=invoice_id,
            customer_id=data['customer_id'],
            total_amount=data.get('total_amount', 0),
            status=data.get('status', 'pending'),
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(invoice_response.dump(invoice)), 200


@bp.route('/invoices/<int:invoice_id>', methods=['DELETE'])
@jwt_required
def delete_invoice(invoice_id):
    """
    Delete an invoice
    ---
    delete:
      summary: Delete an invoice by ID
      parameters:
        - name: invoice_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Billing
      responses:
        204:
          description: Deleted
        404:
          description: Not found
    """
    existing = billing_service.get_invoice(invoice_id)
    if not existing:
        return jsonify({'message': 'Invoice not found'}), 404
    billing_service.delete_invoice(invoice_id)
    return '', 204


@bp.route('/invoices/<int:invoice_id>/items', methods=['GET'])
def list_items(invoice_id):
    """
    List items for an invoice
    ---
    get:
      summary: List invoice items
      parameters:
        - name: invoice_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Billing
      responses:
        200:
          description: List of items
    """
    items = billing_service.list_items(invoice_id)
    return jsonify(item_response.dump(items, many=True)), 200


@bp.route('/invoices/<int:invoice_id>/items', methods=['POST'])
@jwt_required
def add_item(invoice_id):
    """
    Add an item to an invoice
    ---
    post:
      summary: Add an item to an invoice
      parameters:
        - name: invoice_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/InvoiceItemRequest'
      tags:
        - Billing
      responses:
        201:
          description: Created
        400:
          description: Invalid input
    """
    data = request.get_json()
    errors = item_request.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        item = billing_service.add_item(
            invoice_id=invoice_id,
            product_id=data['product_id'],
            quantity=data.get('quantity', 1),
            unit_price=data.get('unit_price', 0),
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(item_response.dump(item)), 201


@bp.route('/invoices/<int:invoice_id>/payments', methods=['GET'])
def list_payments(invoice_id):
    """
    List payments for an invoice
    ---
    get:
      summary: List payment transactions
      parameters:
        - name: invoice_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Billing
      responses:
        200:
          description: List of payments
    """
    payments = billing_service.list_payments(invoice_id)
    return jsonify(payment_response.dump(payments, many=True)), 200


@bp.route('/invoices/<int:invoice_id>/payments', methods=['POST'])
@jwt_required
def add_payment(invoice_id):
    """
    Add a payment to an invoice
    ---
    post:
      summary: Record a payment transaction
      parameters:
        - name: invoice_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PayTransactionRequest'
      tags:
        - Billing
      responses:
        201:
          description: Created
        400:
          description: Invalid input
    """
    data = request.get_json()
    errors = payment_request.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        payment = billing_service.add_payment(
            invoice_id=invoice_id,
            amount=data['amount'],
            payment_method=data['payment_method'],
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(payment_response.dump(payment)), 201


@bp.route('/customers', methods=['GET'])
def list_customers():
    """
    List customers
    ---
    get:
      summary: List all customers
      tags:
        - Billing
      responses:
        200:
          description: List of customers
    """
    customers = billing_service.list_customers()
    return jsonify(paginate_list(customers, customer_response)), 200


@bp.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """
    Get customer by ID
    ---
    get:
      summary: Get a customer by ID
      parameters:
        - name: customer_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Billing
      responses:
        200:
          description: Customer object
        404:
          description: Not found
    """
    customer = billing_service.get_customer(customer_id)
    if not customer:
        return jsonify({'message': 'Customer not found'}), 404
    return jsonify(customer_response.dump(customer)), 200


@bp.route('/customers', methods=['POST'])
@jwt_required
def create_customer():
    """
    Create a new customer
    ---
    post:
      summary: Create a new customer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CustomerRequest'
      tags:
        - Billing
      responses:
        201:
          description: Created
        400:
          description: Invalid input
    """
    data = request.get_json()
    errors = customer_request.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        customer = billing_service.create_customer(
            customer_name=data['customer_name'],
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(customer_response.dump(customer)), 201


@bp.route('/customers/<int:customer_id>', methods=['PUT'])
@jwt_required
def update_customer(customer_id):
    """
    Update a customer
    ---
    put:
      summary: Update a customer by ID
      parameters:
        - name: customer_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CustomerRequest'
      tags:
        - Billing
      responses:
        200:
          description: Updated
        400:
          description: Invalid input
        404:
          description: Not found
    """
    existing = billing_service.get_customer(customer_id)
    if not existing:
        return jsonify({'message': 'Customer not found'}), 404
    data = request.get_json()
    errors = customer_request.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        customer = billing_service.update_customer(
            customer_id=customer_id,
            customer_name=data['customer_name'],
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(customer_response.dump(customer)), 200


@bp.route('/customers/<int:customer_id>', methods=['DELETE'])
@jwt_required
def delete_customer(customer_id):
    """
    Delete a customer
    ---
    delete:
      summary: Delete a customer by ID
      parameters:
        - name: customer_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Billing
      responses:
        204:
          description: Deleted
        404:
          description: Not found
    """
    existing = billing_service.get_customer(customer_id)
    if not existing:
        return jsonify({'message': 'Customer not found'}), 404
    billing_service.delete_customer(customer_id)
    return '', 204


@bp.route('/products', methods=['GET'])
def list_products():
    """
    List products
    ---
    get:
      summary: List all products
      tags:
        - Billing
      responses:
        200:
          description: List of products
    """
    products = billing_service.list_products()
    return jsonify(paginate_list(products, product_response)), 200


@bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    Get product by ID
    ---
    get:
      summary: Get a product by ID
      parameters:
        - name: product_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Billing
      responses:
        200:
          description: Product object
        404:
          description: Not found
    """
    product = billing_service.get_product(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    return jsonify(product_response.dump(product)), 200


@bp.route('/products', methods=['POST'])
@jwt_required
def create_product():
    """
    Create a new product
    ---
    post:
      summary: Create a new product
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ProductRequest'
      tags:
        - Billing
      responses:
        201:
          description: Created
        400:
          description: Invalid input
    """
    data = request.get_json()
    errors = product_request.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        product = billing_service.create_product(
            product_name=data['product_name'],
            description=data.get('description'),
            product_code=data.get('product_code'),
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(product_response.dump(product)), 201


@bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required
def update_product(product_id):
    """
    Update a product
    ---
    put:
      summary: Update a product by ID
      parameters:
        - name: product_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ProductRequest'
      tags:
        - Billing
      responses:
        200:
          description: Updated
        400:
          description: Invalid input
        404:
          description: Not found
    """
    existing = billing_service.get_product(product_id)
    if not existing:
        return jsonify({'message': 'Product not found'}), 404
    data = request.get_json()
    errors = product_request.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        product = billing_service.update_product(
            product_id=product_id,
            product_name=data['product_name'],
            description=data.get('description'),
            product_code=data.get('product_code'),
        )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    return jsonify(product_response.dump(product)), 200


@bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required
def delete_product(product_id):
    """
    Delete a product
    ---
    delete:
      summary: Delete a product by ID
      parameters:
        - name: product_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Billing
      responses:
        204:
          description: Deleted
        404:
          description: Not found
    """
    existing = billing_service.get_product(product_id)
    if not existing:
        return jsonify({'message': 'Product not found'}), 404
    billing_service.delete_product(product_id)
    return '', 204
