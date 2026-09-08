class OrderItem:
    """
    One line item within an order: a product, a quantity,
    and the price at the time it was confirmed.

    Notice price_at_purchase starts as None — it isn't known
    until confirm() actually happens.
    """

    def __init__(self, product_id, quantity):
        self.product_id = product_id
        self.quantity = quantity
        self.price_at_purchase = None   # set during Order.confirm()

    def subtotal(self):
        """
        Return quantity * price_at_purchase.
        Think about: what should this return if the order hasn't
        been confirmed yet and price_at_purchase is still None?
        """
        pass


class Order:
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"

    def __init__(self, order_id, customer_name):
        # store order_id, customer_name, an empty list of OrderItems,
        # status = STATUS_PENDING, and a created_at timestamp (datetime.now())
        pass

    def add_item(self, product_id, quantity):
        """
        Add an OrderItem to this order.
        Raise InvalidOrderStatusError if status is not pending
        (can't add items to a confirmed or cancelled order).
        Raise InvalidQuantityError if quantity <= 0.
        """
        pass

    def confirm(self, inventory):
        """
        The core transaction method. For each item in this order:
          1. Look up the current Product in `inventory`
          2. Check stock is sufficient (inventory.reduce_stock handles this,
             or check explicitly first — your call)
          3. Lock in item.price_at_purchase from the product's CURRENT price
          4. Reduce inventory stock for that product

        Then set status = STATUS_CONFIRMED.

        Raise EmptyOrderError if there are no items.
        Raise InvalidOrderStatusError if already confirmed/cancelled.
        Raise OutOfStockError if any item can't be fulfilled — and
        think carefully here: if item 3 of 5 fails, what happens to
        the stock already reduced for items 1 and 2? This is a real
        edge case worth deciding deliberately.
        """
        pass

    def cancel(self, inventory):
        """
        If status is pending: just mark as cancelled, nothing to restock.
        If status is confirmed: restock every item's quantity back into
        inventory, THEN mark as cancelled.
        Raise InvalidOrderStatusError if already cancelled.
        """
        pass

    def total(self):
        """
        Sum of all item subtotals.
        Good spot to use sum() with a generator expression, or reduce().
        """
        pass

    def __str__(self):
        pass

    def __repr__(self):
        pass