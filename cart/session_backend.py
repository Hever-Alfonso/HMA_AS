from .base import CartBackend
from .cart import Cart


class SessionCartBackend(CartBackend):
    """Adaptador del carrito almacenado en sesión."""

    def __init__(self, session):
        self.session = session
        self.cart = Cart(type("Request", (), {"session": session})())

    def add_item(self, product, size, quantity) -> None:
        self.cart.add(product, size, cantidad=quantity)

    def set_item(self, product, size, quantity) -> None:
        self.cart.add(product, size, cantidad=quantity, override_cantidad=True)

    def remove_item(self, product, size) -> None:
        self.cart.remove(product, size)

    def update_item(self, product, size, quantity) -> None:
        self.cart.update(product, size, cantidad=quantity)

    def get_items(self) -> list:
        return list(self.cart)

    def clear(self) -> None:
        self.cart.clear()

    def __len__(self):
        return len(self.cart)
