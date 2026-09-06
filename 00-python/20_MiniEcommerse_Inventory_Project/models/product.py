from abc import ABC, abstractmethod


class Product(ABC):
    def __init__(self, product_id, name, price, quantity, category):
        # TODO: store product_id, name, category directly.
        # For price and quantity, decide: set via self.price = price
        # (routes through your validating setters) or set the private
        # attribute directly? Which gives you validation for free?
        pass

    @property
    def price(self):
        pass

    @price.setter
    def price(self, value):
        # raise ValueError if value < 0
        pass

    @property
    def quantity(self):
        pass

    @quantity.setter
    def quantity(self, value):
        # raise ValueError if value < 0
        pass

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