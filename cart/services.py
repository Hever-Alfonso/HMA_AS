from django.db import transaction

from products.models import StockPorTalla

from .cart import Cart
from .models import Carrito, ItemCarrito


class CartService:
    """Centraliza reglas de negocio del carrito de sesión."""

    @staticmethod
    def validate_item(producto, talla, cantidad):
        if not talla:
            raise ValueError("Debes seleccionar una talla.")
        if talla not in StockPorTalla.Talla.values:
            raise ValueError("La talla seleccionada no es válida.")
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser positiva.")

        stock = StockPorTalla.objects.filter(producto=producto, talla=talla).first()
        available_stock = stock.cantidad if stock else 0

        if available_stock <= 0:
            raise ValueError(f"La talla {talla} está agotada.")
        if cantidad > available_stock:
            raise ValueError(f"No hay suficiente stock para la talla {talla}.")

    @classmethod
    def add_item(cls, request, producto, talla, cantidad):
        cls.validate_item(producto, talla, cantidad)
        Cart(request).add(producto=producto, talla=talla, cantidad=cantidad)

    @classmethod
    def update_item(cls, request, producto, talla, cantidad):
        cart = Cart(request)
        if cantidad <= 0:
            cart.remove(producto=producto, talla=talla)
            return
        cls.validate_item(producto, talla, cantidad)
        cart.update(producto=producto, talla=talla, cantidad=cantidad)

    @staticmethod
    def remove_item(request, producto, talla):
        Cart(request).remove(producto=producto, talla=talla)


class CartMergeService:
    """Sincroniza carrito de sesión y BD con precedencia para la BD."""

    @staticmethod
    @transaction.atomic
    def merge_session_into_db(request, user):
        session_cart = Cart(request)
        db_cart, _ = Carrito.objects.get_or_create(
            usuario=user,
            defaults={'estado': Carrito.EstadoCarrito.ACTIVO},
        )

        if db_cart.estado != Carrito.EstadoCarrito.ACTIVO:
            db_cart.estado = Carrito.EstadoCarrito.ACTIVO
            db_cart.save(update_fields=['estado'])

        existing_keys = {
            f"{item.producto_id}:{item.talla}"
            for item in db_cart.items.select_related('producto')
        }

        for session_item in session_cart:
            key = f"{session_item['producto'].id}:{session_item['talla']}"
            if key in existing_keys:
                continue

            ItemCarrito.objects.create(
                carrito=db_cart,
                producto=session_item['producto'],
                talla=session_item['talla'],
                cantidad=session_item['cantidad'],
                precio_unitario=session_item['precio_unitario'],
            )

        session_cart.clear()
        for db_item in db_cart.items.select_related('producto'):
            session_cart.add(
                db_item.producto,
                db_item.talla,
                cantidad=db_item.cantidad,
                override_cantidad=True,
            )
