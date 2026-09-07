from abc import ABC, abstractmethod


class Product(ABC):
    def __init__(self, product_id, name, price, quantity, category):
        self.product_id  =  product_id
        self.name = name
        self.category = category

        self.price = price
        self.quantity = quantity
        pass

    @property
    def price(self):
        return  self._price

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
        if value <= 0:
            raise ValueError("Quantity must be > 0")
        self._quantity = value

    @abstractmethod
    def shipping_info(self):
        pass

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def __eq__(self, other):
        # equal if same product_id (check isinstance first)
        pass


class PhysicalProduct(Product):
    def __init__(self, product_id, name, price, quantity, category, weight_kg):
        pass

    def shipping_info(self):
        pass


class DigitalProduct(Product):
    def __init__(self, product_id, name, price, quantity, category, file_size_mb):
        pass

    def shipping_info(self):
        pass