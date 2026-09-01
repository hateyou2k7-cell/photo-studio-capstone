from abc import ABC, abstractmethod
from typing import List, Optional
from .billing import Invoice, InvoiceItem, Customer, Product, PayTransaction


class IInvoiceRepository(ABC):
    @abstractmethod
    def add(self, invoice: Invoice) -> Invoice:
        pass

    @abstractmethod
    def get_by_id(self, invoice_id: int) -> Optional[Invoice]:
        pass

    @abstractmethod
    def list(self, customer_id=None, status=None) -> List[Invoice]:
        pass

    @abstractmethod
    def update(self, invoice: Invoice) -> Invoice:
        pass

    @abstractmethod
    def delete(self, invoice_id: int) -> None:
        pass

    @abstractmethod
    def add_item(self, item: InvoiceItem) -> InvoiceItem:
        pass

    @abstractmethod
    def list_items(self, invoice_id: int) -> List[InvoiceItem]:
        pass

    @abstractmethod
    def delete_item(self, item_id: int) -> None:
        pass

    @abstractmethod
    def add_customer(self, customer: Customer) -> Customer:
        pass

    @abstractmethod
    def get_customer(self, customer_id: int) -> Optional[Customer]:
        pass

    @abstractmethod
    def list_customers(self) -> List[Customer]:
        pass

    @abstractmethod
    def update_customer(self, customer: Customer) -> Customer:
        pass

    @abstractmethod
    def delete_customer(self, customer_id: int) -> None:
        pass

    @abstractmethod
    def add_product(self, product: Product) -> Product:
        pass

    @abstractmethod
    def get_product(self, product_id: int) -> Optional[Product]:
        pass

    @abstractmethod
    def list_products(self) -> List[Product]:
        pass

    @abstractmethod
    def update_product(self, product: Product) -> Product:
        pass

    @abstractmethod
    def delete_product(self, product_id: int) -> None:
        pass

    @abstractmethod
    def add_payment(self, payment: PayTransaction) -> PayTransaction:
        pass

    @abstractmethod
    def list_payments(self, invoice_id: int) -> List[PayTransaction]:
        pass
