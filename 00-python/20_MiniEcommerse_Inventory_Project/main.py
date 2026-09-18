import json
from pathlib import Path

from exceptions import InventoryError, OrderError
from models import DigitalProduct, Inventory, Order, PhysicalProduct

DATA_FILE = Path(__file__).resolve().parent / "data" / "inventory.json"


def ensure_data_file():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")


def load_inventory():
    ensure_data_file()
    inventory = Inventory()

    try:
        raw_data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        raw_data = []

    for item in raw_data:
        product_type = item.get("type")

        if product_type == "PhysicalProduct":
            product = PhysicalProduct.from_dict(item)
        elif product_type == "DigitalProduct":
            product = DigitalProduct.from_dict(item)
        else:
            continue

        inventory.add_product(product)

    return inventory


def save_inventory(inventory):
    ensure_data_file()
    payload = [product.to_dict() for product in inventory]
    DATA_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def seed_inventory():
    inventory = Inventory()

    products = [
        PhysicalProduct("P001", "Wireless Mouse", 25.0, 12, "Electronics", 0.2),
        PhysicalProduct("P002", "Mechanical Keyboard", 70.0, 8, "Electronics", 1.5),
        DigitalProduct("D001", "Python Guide", 19.99, 25, "Books", 7),
        DigitalProduct("D002", "AI Crash Course", 29.99, 15, "Books", 12),
    ]

    for product in products:
        inventory.add_product(product)

    save_inventory(inventory)
    return inventory


def show_inventory(inventory):
    print("\nCurrent inventory:")
    if len(inventory) == 0:
        print("  No products available.")
        return

    for product in inventory:
        print(f"  - {product.product_id}: {product.name} | {product.category} | "
              f"{product.quantity} in stock | ${product.price:.2f}")


def add_product_to_inventory(inventory):
    print("\nAdd a product")
    product_id = input("Product ID: ").strip()
    name = input("Name: ").strip()
    category = input("Category: ").strip()

    try:
        price = float(input("Price: ").strip())
        quantity = int(input("Quantity: ").strip())
    except ValueError:
        print("Invalid numeric input. Please try again.")
        return

    product_type = input("Type (physical/digital): ").strip().lower()

    try:
        if product_type == "physical":
            weight = float(input("Weight in kg: ").strip())
            product = PhysicalProduct(product_id, name, price, quantity, category, weight)
        elif product_type == "digital":
            file_size = float(input("File size in MB: ").strip())
            product = DigitalProduct(product_id, name, price, quantity, category, file_size)
        else:
            print("Invalid product type.")
            return

        inventory.add_product(product)
        save_inventory(inventory)
        print(f"Added {product.name} successfully.")
    except (ValueError, InventoryError) as exc:
        print(f"Could not add product: {exc}")


def place_order(inventory):
    print("\nCreate a new order")
    order_id = input("Order ID: ").strip()
    customer_name = input("Customer name: ").strip()
    order = Order(order_id, customer_name)

    while True:
        product_id = input("Add product ID (or 'done'): ").strip()
        if product_id.lower() == "done":
            break

        try:
            qty = int(input("Quantity: ").strip())
        except ValueError:
            print("Quantity must be a number.")
            continue

        try:
            order.add_item(product_id, qty)
            print(f"Added {qty} unit(s) of product {product_id}.")
        except (InventoryError, OrderError, ValueError) as exc:
            print(f"Could not add item: {exc}")

    try:
        order.confirm(inventory)
        save_inventory(inventory)
        print(f"Order {order_id} confirmed successfully.")
        print(f"Total: ${order.total():.2f}")
    except (InventoryError, OrderError) as exc:
        print(f"Order failed: {exc}")


def main():
    inventory = load_inventory()

    if len(inventory) == 0:
        inventory = seed_inventory()

    while True:
        print("\n=== Mini Inventory Management System ===")
        print("1. View inventory")
        print("2. Add product")
        print("3. Place order")
        print("4. Save and exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            show_inventory(inventory)
        elif choice == "2":
            add_product_to_inventory(inventory)
        elif choice == "3":
            place_order(inventory)
        elif choice == "4":
            save_inventory(inventory)
            print("Inventory saved. Goodbye!")
            break
        else:
            print("Invalid option. Please choose 1, 2, 3 or 4.")


if __name__ == "__main__":
    main()
