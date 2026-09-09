from datetime import datetime
from .exceptions import (
    InvalidOrderStatusError,
    InvalidQuantityError,
    EmptyOrderError,
    OutOfStockError,
)


class OrderItem:
    """
    One line item within an order: a product, a quantity,
    and the price at the time it was confirmed.
    """

    def __init__(self, product_id, quantity):
        self.product_id = product_id
        self.quantity = quantity
        self.price_at_purchase = None   # set during Order.confirm()

    def subtotal(self):
        """
        Return quantity * price_at_purchase.
        If the order hasn't been confirmed yet, price_at_purchase is
        still None — there's no meaningful subtotal yet, so return 0
        rather than crashing with a TypeError (None * quantity).
        """
        if self.price_at_purchase is None:
            return 0
        return self.quantity * self.price_at_purchase

    def __repr__(self):
        return (
            f"OrderItem(product_id={self.product_id!r}, "
            f"quantity={self.quantity}, "
            f"price_at_purchase={self.price_at_purchase})"
        )


class Order:
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"

    def __init__(self, order_id, customer_name):
        self.order_id = order_id
        self.customer_name = customer_name
        self.items = []
        self.status = Order.STATUS_PENDING
        self.created_at = datetime.now()

    def add_item(self, product_id, quantity):
        """
        Add an OrderItem to this order.
        """
        if self.status != Order.STATUS_PENDING:
            raise InvalidOrderStatusError(
                f"Cannot add items to an order with status '{self.status}'"
            )

        if quantity <= 0:
            raise InvalidQuantityError("Item quantity must be greater than 0")

        self.items.append(OrderItem(product_id, quantity))

    def confirm(self, inventory):
        """
        The core transaction method — validates everything BEFORE
        making any changes, so a failure partway through never
        leaves inventory in a half-reduced, inconsistent state.
        """
        if self.status != Order.STATUS_PENDING:
            raise InvalidOrderStatusError(
                f"Cannot confirm an order with status '{self.status}'"
            )

        if not self.items:
            raise EmptyOrderError("Cannot confirm an order with no items")

        # PASS 1 — validate every item can actually be fulfilled.
        # Nothing is changed yet; this just checks and raises early
        # if ANY item would fail, before any stock is touched.
        for item in self.items:
            product = inventory.get_product(item.product_id)
            if item.quantity > product.quantity:
                raise OutOfStockError(
                    f"Cannot confirm order: requested {item.quantity} of "
                    f"'{product.name}', only {product.quantity} available"
                )

        # PASS 2 — everything validated, now it's safe to actually
        # commit: lock in prices and reduce stock for real.
        for item in self.items:
            product = inventory.get_product(item.product_id)
            item.price_at_purchase = product.price
            inventory.reduce_stock(item.product_id, item.quantity)

        self.status = Order.STATUS_CONFIRMED

    def cancel(self, inventory):
        """
        If pending: just mark cancelled, nothing to restock.
        If confirmed: restock every item back into inventory first.
        """
        if self.status == Order.STATUS_CANCELLED:
            raise InvalidOrderStatusError("Order is already cancelled")

        if self.status == Order.STATUS_CONFIRMED:
            for item in self.items:
                inventory.restock_product(item.product_id, item.quantity)

        self.status = Order.STATUS_CANCELLED

    def total(self):
        """
        Sum of all item subtotals.
        """
        return sum(item.subtotal() for item in self.items)

    def __str__(self):
        return (
            f"Order #{self.order_id} - {self.customer_name} "
            f"[{self.status}] - ${self.total():.2f}"
        )

    def __repr__(self):
        return (
            f"Order(order_id={self.order_id!r}, "
            f"customer_name={self.customer_name!r}, "
            f"status={self.status!r}, items={len(self.items)})"
        )