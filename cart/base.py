from abc import ABC, abstractmethod


class CartBackend(ABC):
    """Define el contrato común para carritos de sesión y base de datos."""

    @abstractmethod
    def add_item(self, product, size, quantity) -> None:
        pass

    @abstractmethod
    def get_items(self) -> list:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass
