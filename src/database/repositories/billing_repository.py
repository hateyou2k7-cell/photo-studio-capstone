from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from business.models.ibilling_repository import IInvoiceRepository
from business.models.billing import Invoice, InvoiceItem, Customer, Product, PayTransaction
from database.models.sell.sell_invoice_model import SellInvoiceModel, SellInvoiceItemModel
from database.models.sell.sell_customer_model import SellCustomerModel
from database.models.sell.sell_product_model import SellProductModel
from database.models.pay.pay_tran_model import PayTranModel
from database.databases.factory_database import FactoryDatabase as db_factory
import uuid


class InvoiceRepository(IInvoiceRepository):
    def __init__(self, session: Session = None):
        self.session = session or db_factory.get_database('POSTGREE').session

    def _generate_invoice_code(self):
        return f'INV-{uuid.uuid4().hex[:8].upper()}'

    def add(self, invoice: Invoice) -> SellInvoiceModel:
        try:
            model = SellInvoiceModel(
                customer_id=invoice.customer_id,
                invoice_date=invoice.invoice_date or datetime.utcnow(),
                total_amount=invoice.total_amount,
                status=invoice.status or 'pending',
                invoice_code=invoice.invoice_code or self._generate_invoice_code(),
                blank_amount=invoice.blank_amount,
                paid_amount=invoice.paid_amount,
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except Exception:
            self.session.rollback()
            raise ValueError('Could not create invoice')
        finally:
            self.session.close()

    def get_by_id(self, invoice_id: int) -> Optional[SellInvoiceModel]:
        return self.session.query(SellInvoiceModel).filter_by(id=invoice_id).first()

    def list(self, customer_id=None, status=None) -> List[SellInvoiceModel]:
        query = self.session.query(SellInvoiceModel)
        if customer_id is not None:
            query = query.filter_by(customer_id=customer_id)
        if status is not None:
            query = query.filter_by(status=status)
        return query.order_by(SellInvoiceModel.created_at.desc()).all()

    def update(self, invoice: Invoice) -> SellInvoiceModel:
        try:
            existing = self.session.query(SellInvoiceModel).filter_by(id=invoice.id).first()
            if not existing:
                raise ValueError('Invoice not found')
            existing.customer_id = invoice.customer_id
            existing.invoice_date = invoice.invoice_date
            existing.total_amount = invoice.total_amount
            existing.status = invoice.status
            existing.blank_amount = invoice.blank_amount
            existing.paid_amount = invoice.paid_amount
            existing.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(existing)
            return existing
        except ValueError:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Could not update invoice')
        finally:
            self.session.close()

    def delete(self, invoice_id: int) -> None:
        try:
            model = self.session.query(SellInvoiceModel).filter_by(id=invoice_id).first()
            if model:
                self.session.query(SellInvoiceItemModel).filter_by(invoice_id=invoice_id).delete()
                self.session.delete(model)
                self.session.commit()
            else:
                raise ValueError('Invoice not found')
        except Exception:
            self.session.rollback()
            raise ValueError('Invoice not found')
        finally:
            self.session.close()

    def add_item(self, item: InvoiceItem) -> SellInvoiceItemModel:
        try:
            model = SellInvoiceItemModel(
                invoice_id=item.invoice_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except Exception:
            self.session.rollback()
            raise ValueError('Could not add invoice item')
        finally:
            self.session.close()

    def list_items(self, invoice_id: int) -> List[SellInvoiceItemModel]:
        return self.session.query(SellInvoiceItemModel).filter_by(invoice_id=invoice_id).all()

    def delete_item(self, item_id: int) -> None:
        try:
            model = self.session.query(SellInvoiceItemModel).filter_by(id=item_id).first()
            if model:
                self.session.delete(model)
                self.session.commit()
            else:
                raise ValueError('Invoice item not found')
        except Exception:
            self.session.rollback()
            raise ValueError('Invoice item not found')
        finally:
            self.session.close()

    def add_customer(self, customer: Customer) -> SellCustomerModel:
        try:
            model = SellCustomerModel(
                customer_name=customer.customer_name,
                email=customer.email,
                phone=customer.phone,
                address=customer.address,
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except Exception:
            self.session.rollback()
            raise ValueError('Could not create customer')
        finally:
            self.session.close()

    def get_customer(self, customer_id: int) -> Optional[SellCustomerModel]:
        return self.session.query(SellCustomerModel).filter_by(id=customer_id).first()

    def list_customers(self) -> List[SellCustomerModel]:
        return self.session.query(SellCustomerModel).all()

    def update_customer(self, customer: Customer) -> SellCustomerModel:
        try:
            existing = self.session.query(SellCustomerModel).filter_by(id=customer.id).first()
            if not existing:
                raise ValueError('Customer not found')
            existing.customer_name = customer.customer_name
            existing.email = customer.email
            existing.phone = customer.phone
            existing.address = customer.address
            existing.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(existing)
            return existing
        except ValueError:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Could not update customer')
        finally:
            self.session.close()

    def delete_customer(self, customer_id: int) -> None:
        try:
            model = self.session.query(SellCustomerModel).filter_by(id=customer_id).first()
            if model:
                self.session.delete(model)
                self.session.commit()
            else:
                raise ValueError('Customer not found')
        except Exception:
            self.session.rollback()
            raise ValueError('Customer not found')
        finally:
            self.session.close()

    def add_product(self, product: Product) -> SellProductModel:
        try:
            model = SellProductModel(
                product_name=product.product_name,
                description=product.description,
                product_code=product.product_code,
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except Exception:
            self.session.rollback()
            raise ValueError('Could not create product')
        finally:
            self.session.close()

    def get_product(self, product_id: int) -> Optional[SellProductModel]:
        return self.session.query(SellProductModel).filter_by(id=product_id).first()

    def list_products(self) -> List[SellProductModel]:
        return self.session.query(SellProductModel).all()

    def update_product(self, product: Product) -> SellProductModel:
        try:
            existing = self.session.query(SellProductModel).filter_by(id=product.id).first()
            if not existing:
                raise ValueError('Product not found')
            existing.product_name = product.product_name
            existing.description = product.description
            existing.product_code = product.product_code
            existing.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(existing)
            return existing
        except ValueError:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise ValueError('Could not update product')
        finally:
            self.session.close()

    def delete_product(self, product_id: int) -> None:
        try:
            model = self.session.query(SellProductModel).filter_by(id=product_id).first()
            if model:
                self.session.delete(model)
                self.session.commit()
            else:
                raise ValueError('Product not found')
        except Exception:
            self.session.rollback()
            raise ValueError('Product not found')
        finally:
            self.session.close()

    def add_payment(self, payment: PayTransaction) -> PayTranModel:
        try:
            model = PayTranModel(
                invoice_id=payment.invoice_id,
                amount=payment.amount,
                payment_method=payment.payment_method,
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except Exception:
            self.session.rollback()
            raise ValueError('Could not add payment')
        finally:
            self.session.close()

    def list_payments(self, invoice_id: int) -> List[PayTranModel]:
        return self.session.query(PayTranModel).filter_by(invoice_id=invoice_id).all()
