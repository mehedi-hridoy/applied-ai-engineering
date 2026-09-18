from abc import ABC, abstractmethod


class Product(ABC):
    def __init__(self, product_id, name, price, quantity, category):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.price = price
        self.quantity = quantity

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if value < 0:
            raise ValueError("Price must be >= 0")
        self._price = value

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        if value < 0:
            raise ValueError("Quantity must be >= 0")
        self._quantity = value

    @abstractmethod
    def shipping_info(self):
        pass

    def to_dict(self):
        """Return a plain dict representing this product for JSON storage."""
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data):
        """Create a product instance from a dictionary."""
        product_type = data.get("type")
        if product_type == "PhysicalProduct":
            return PhysicalProduct(
                data["product_id"],
                data["name"],
                data["price"],
                data["quantity"],
                data["category"],
                data["weight_kg"],
            )
        if product_type == "DigitalProduct":
            return DigitalProduct(
                data["product_id"],
                data["name"],
                data["price"],
                data["quantity"],
                data["category"],
                data["file_size_mb"],
            )
        raise ValueError(f"Unsupported product type: {product_type!r}")

    def __str__(self):
        return f"{self.name} - ${self.price:.2f} ({self.quantity} in stock)"

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"product_id={self.product_id!r}, name={self.name!r}, "
            f"price={self.price}, quantity={self.quantity})"
        )

    def __eq__(self, other):
        if not isinstance(other, Product):
            return NotImplemented
        return self.product_id == other.product_id


class PhysicalProduct(Product):
    def __init__(self, product_id, name, price, quantity, category, weight_kg):
        super().__init__(product_id, name, price, quantity, category)
        self.weight_kg = weight_kg

    def shipping_info(self):
        return f"Ships physically, weighs {self.weight_kg}kg"

    def to_dict(self):
        data = super().to_dict()
        data["type"] = "PhysicalProduct"
        data["weight_kg"] = self.weight_kg
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["product_id"],
            data["name"],
            data["price"],
            data["quantity"],
            data["category"],
            data["weight_kg"],
        )


class DigitalProduct(Product):
    def __init__(self, product_id, name, price, quantity, category, file_size_mb):
        super().__init__(product_id, name, price, quantity, category)
        self.file_size_mb = file_size_mb

    def shipping_info(self):
        return f"Digital delivery, {self.file_size_mb}MB download"

    def to_dict(self):
        data = super().to_dict()
        data["type"] = "DigitalProduct"
        data["file_size_mb"] = self.file_size_mb
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["product_id"],
            data["name"],
            data["price"],
            data["quantity"],
            data["category"],
            data["file_size_mb"],
        )
