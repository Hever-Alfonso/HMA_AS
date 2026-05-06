from .base import CartBackend
from .models import Carrito, ItemCarrito


class DatabaseCartBackend(CartBackend):
    """Adaptador del carrito persistido para un usuario autenticado."""

    def __init__(self, user):
        self.user = user
        self.cart, _ = Carrito.objects.get_or_create(
            usuario=user,
            defaults={'estado': Carrito.EstadoCarrito.ACTIVO},
        )
        if self.cart.estado != Carrito.EstadoCarrito.ACTIVO:
            self.cart.estado = Carrito.EstadoCarrito.ACTIVO
            self.cart.save(update_fields=['estado'])

    def add_item(self, product, size, quantity) -> None:
        item, created = ItemCarrito.objects.get_or_create(
            carrito=self.cart,
            producto=product,
            talla=size,
            defaults={
                'cantidad': quantity,
                'precio_unitario': product.precio,
            },
        )
        if not created:
            item.cantidad += quantity
            item.save(update_fields=['cantidad'])

    def set_item(self, product, size, quantity) -> None:
        item, _ = ItemCarrito.objects.get_or_create(
            carrito=self.cart,
            producto=product,
            talla=size,
            defaults={
                'cantidad': quantity,
                'precio_unitario': product.precio,
            },
        )
        item.cantidad = quantity
        item.save(update_fields=['cantidad'])

    def get_items(self) -> list:
        return [
            {
                'key': f'{item.producto_id}:{item.talla}',
                'producto': item.producto,
                'talla': item.talla,
                'cantidad': item.cantidad,
                'precio_unitario': item.precio_unitario,
                'subtotal': item.subtotal,
            }
            for item in self.cart.items.select_related('producto')
        ]

    def clear(self) -> None:
        self.cart.limpiar()

    def mark_converted(self) -> None:
        self.cart.estado = Carrito.EstadoCarrito.CONVERTIDO
        self.cart.save(update_fields=['estado'])
