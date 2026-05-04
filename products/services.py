from django.db import transaction

from .models import StockPorTalla


class InventoryService:
    """Gestiona validaciones y cambios de inventario por talla."""

    @staticmethod
    def validate_size(size):
        if not size:
            raise ValueError("Debes seleccionar una talla.")
        if size not in StockPorTalla.Talla.values:
            raise ValueError("La talla seleccionada no es válida.")

    @staticmethod
    def get_stock(product, size, for_update=False):
        InventoryService.validate_size(size)
        queryset = StockPorTalla.objects
        if for_update:
            queryset = queryset.select_for_update()
        return queryset.filter(producto=product, talla=size).first()

    @classmethod
    def validate_available(cls, product, size, quantity):
        cls.validate_size(size)
        if quantity <= 0:
            raise ValueError("La cantidad debe ser positiva.")

        stock = cls.get_stock(product, size)
        available_stock = stock.cantidad if stock else 0

        if available_stock <= 0:
            raise ValueError(f"La talla {size} está agotada.")
        if quantity > available_stock:
            raise ValueError(f"No hay suficiente stock para la talla {size}.")

    @classmethod
    @transaction.atomic
    def decrease_stock(cls, product, size, quantity):
        cls.validate_size(size)
        if quantity <= 0:
            raise ValueError("La cantidad debe ser positiva.")

        stock = cls.get_stock(product, size, for_update=True)
        if stock is None:
            raise ValueError(f"La talla {size} está agotada.")
        if not stock.esta_disponible(quantity):
            raise ValueError(
                f"Stock insuficiente para {product.nombre} "
                f"talla {size}. (Quedan {stock.cantidad})"
            )

        stock.disminuir(quantity)
        return stock

    @classmethod
    @transaction.atomic
    def increase_stock(cls, product, size, quantity):
        cls.validate_size(size)
        if quantity <= 0:
            raise ValueError("La cantidad debe ser positiva.")

        stock = cls.get_stock(product, size, for_update=True)
        if stock is None:
            stock = StockPorTalla.objects.create(producto=product, talla=size, cantidad=0)
        stock.aumentar(quantity)
        return stock
