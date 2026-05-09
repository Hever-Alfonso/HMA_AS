from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from cart.cart import Cart
from cart.db_backend import DatabaseCartBackend
from .models import Orden, ItemOrden
from .shipping import ShippingRateProviderFactory
from products.services import InventoryService


class OrdenService:
    """Servicio para manejar lógica de negocio de órdenes (SRP)."""

    @staticmethod
    @transaction.atomic
    def crear_desde_carrito(usuario, request, datos_envio):
        """
        Crea una orden desde el carrito de sesión con validación atómica de stock.
        Usa select_for_update() para prevenir overselling.
        """
        session_cart = Cart(request)

        if len(session_cart) == 0:
            raise ValueError(_("El carrito está vacío."))

        shipping_provider = ShippingRateProviderFactory.create()
        costo_envio = shipping_provider.calculate(datos_envio)

        # 1. Crear Orden
        orden = Orden.objects.create(
            usuario=usuario,
            direccion_envio=datos_envio.get('direccion_envio', ''),
            ciudad=datos_envio.get('ciudad', ''),
            codigo_postal=datos_envio.get('codigo_postal', ''),
            telefono_contacto=datos_envio.get('telefono_contacto', ''),
            costo_envio=costo_envio,
        )
        try:
            orden.full_clean()
        except ValidationError as exc:
            raise ValueError(_("Los datos de envío no son válidos.")) from exc

        # 2. Validar stock y crear items atómicamente
        for cart_item in session_cart:
            producto_obj = cart_item['producto']
            talla = cart_item['talla']
            cantidad_req = cart_item['cantidad']

            InventoryService.decrease_stock(producto_obj, talla, cantidad_req)

            ItemOrden.objects.create(
                orden=orden,
                producto=producto_obj,
                talla=talla,
                cantidad=cantidad_req,
                precio_unitario=cart_item['precio_unitario'],
                subtotal=cart_item['subtotal']
            )

        orden.calcular_total()
        orden.marcar_como_pagada()

        # 3. Limpiar sesión y BD del carrito
        session_cart.clear()
        db_cart = DatabaseCartBackend(usuario)
        db_cart.clear()
        db_cart.mark_converted()

        return orden

    @staticmethod
    @transaction.atomic
    def cancelar_orden(orden):
        """Cancela la orden y restablece el stock atómicamente."""
        if orden.estado == Orden.EstadoOrden.CANCELADA:
            return

        # Recuperar stock bloqueando los registros
        for item in orden.items.all():
            InventoryService.increase_stock(item.producto, item.talla, item.cantidad)

        orden.cancelar()
