from models.inventory import Inventory
from models.order import Order
from models.product import DigitalProduct, PhysicalProduct
from exceptions import DuplicateProductError, OutOfStockError, ProductNotFoundError


def test_inventory_add_and_duplicate_rejection():
    inventory = Inventory()
    product = PhysicalProduct("P001", "Mouse", 25.0, 10, "Electronics", 0.3)

    inventory.add_product(product)

    assert inventory.get_product("P001") == product
    try:
        inventory.add_product(product)
        assert False, "Expected DuplicateProductError"
    except DuplicateProductError:
        pass


def test_order_confirmation_reduces_stock_and_sets_status():
    inventory = Inventory()
    product = DigitalProduct("D001", "Guide", 19.99, 5, "Books", 7)
    inventory.add_product(product)

    order = Order("O-100", "Alice")
    order.add_item("D001", 2)
    order.confirm(inventory)

    assert order.status == "confirmed"
    assert inventory.get_product("D001").quantity == 3
    assert order.total() == 39.98


def test_order_confirms_after_validating_stock():
    inventory = Inventory()
    product = PhysicalProduct("P002", "Keyboard", 60.0, 1, "Electronics", 0.8)
    inventory.add_product(product)

    order = Order("O-200", "Bob")
    order.add_item("P002", 2)

    try:
        order.confirm(inventory)
        assert False, "Expected OutOfStockError"
    except OutOfStockError:
        pass

    assert product.quantity == 1
    assert order.status == "pending"


def test_product_serialization_round_trip():
    product = PhysicalProduct("P003", "Monitor", 199.99, 4, "Electronics", 3.5)

    data = product.to_dict()
    rebuilt = PhysicalProduct.from_dict(data)

    assert rebuilt.product_id == product.product_id
    assert rebuilt.name == product.name
    assert rebuilt.weight_kg == product.weight_kg
    assert rebuilt == product


def test_missing_product_lookup_raises():
    inventory = Inventory()

    try:
        inventory.get_product("MISSING")
        assert False, "Expected ProductNotFoundError"
    except ProductNotFoundError:
        pass
