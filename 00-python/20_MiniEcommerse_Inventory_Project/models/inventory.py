from .product import Product
from .exceptions import (
    DuplicateProductError,
    ProductNotFoundError,
    InvalidQuantityError,
    OutOfStockError,
)


class Inventory:
    def __init__(self):
        self._products = {}   # dict: product_id -> Product

    def _get_or_raise(self, product_id):
        """Internal helper: return the product, or raise ProductNotFoundError."""
        product = self._products.get(product_id)
        if product is None:
            raise ProductNotFoundError(f"No product found with ID '{product_id}'")
        return product

    def add_product(self, product):
        """Raise DuplicateProductError if product_id already exists."""
        if not isinstance(product, Product):
            raise TypeError("Only Product instances can be added to Inventory")

        if product.product_id in self._products:
            raise DuplicateProductError(
                f"Product with ID '{product.product_id}' already exists"
            )

        self._products[product.product_id] = product

    def restock_product(self, product_id, amount):
        """
        Increase quantity of an EXISTING product by amount.
        Raise ProductNotFoundError if it doesn't exist.
        Raise InvalidQuantityError if amount <= 0.
        """
        product = self._get_or_raise(product_id)

        if amount <= 0:
            raise InvalidQuantityError("Restock amount must be greater than 0")

        product.quantity += amount

    def remove_product(self, product_id):
        """Raise ProductNotFoundError if it doesn't exist."""
        self._get_or_raise(product_id)
        del self._products[product_id]

    def get_product(self, product_id):
        """Raise ProductNotFoundError if it doesn't exist."""
        return self._get_or_raise(product_id)

    def reduce_stock(self, product_id, quantity):
        """
        Called by Order.confirm() — reduces quantity by `quantity`.
        Raise OutOfStockError if quantity requested > available.
        """
        product = self._get_or_raise(product_id)

        if quantity > product.quantity:
            raise OutOfStockError(
                f"Requested {quantity} of '{product.name}', "
                f"only {product.quantity} available"
            )

        product.quantity -= quantity

    def total_value(self):
        return sum(p.price * p.quantity for p in self._products.values())

    def low_stock_products(self, threshold=5):
        return [p for p in self._products.values() if p.quantity < threshold]

    def categories(self):
        """Return a set of all unique categories currently in stock."""
        return {p.category for p in self._products.values()}

    def __len__(self):
        return len(self._products)

    def __contains__(self, product_id):
        return product_id in self._products

    def __iter__(self):
        return iter(self._products.values())