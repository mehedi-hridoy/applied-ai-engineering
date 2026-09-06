class Inventory:
    def __init__(self):
        # dict keyed by product_id
        pass

    def add_product(self, product):
        """Raise DuplicateProductError if product_id already exists."""
        pass

    def restock_product(self, product_id, amount):
        """
        Increase quantity of an EXISTING product by amount.
        Raise ProductNotFoundError if it doesn't exist.
        Raise InvalidQuantityError if amount <= 0.
        """
        pass

    def remove_product(self, product_id):
        """Raise ProductNotFoundError if it doesn't exist."""
        pass

    def get_product(self, product_id):
        """Raise ProductNotFoundError if it doesn't exist."""
        pass

    def reduce_stock(self, product_id, quantity):
        """
        Called by Order.confirm() — reduces quantity by `quantity`.
        Raise OutOfStockError if quantity requested > available.
        """
        pass

    def total_value(self):
        pass

    def low_stock_products(self, threshold=5):
        pass

    def categories(self):
        """Return a set of all unique categories currently in stock."""
        pass

    def __len__(self):
        pass

    def __contains__(self, product_id):
        pass

    def __iter__(self):
        pass