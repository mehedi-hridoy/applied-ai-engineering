class InventoryError(Exception):
    """Base exception for all inventory-related errors."""
    pass


class ProductNotFoundError(InventoryError):
    """Raised when looking up a product_id that doesn't exist."""
    pass


class DuplicateProductError(InventoryError):
    """Raised when trying to add a product with an ID that already exists."""
    pass


class OutOfStockError(InventoryError):
    """Raised when requested quantity exceeds available stock."""
    pass


class InvalidQuantityError(InventoryError):
    """Raised when a quantity/amount value is invalid (e.g. <= 0)."""
    pass


class OrderError(Exception):
    """Base exception for all order-related errors."""
    pass


class EmptyOrderError(OrderError):
    """Raised when trying to confirm an order with no items."""
    pass


class InvalidOrderStatusError(OrderError):
    """Raised when an operation isn't allowed given the order's current status."""
    pass