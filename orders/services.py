from django.db import transaction
from cart.cart import Cart
from cart.models import Carrito
from .models import Orden, ItemOrden
from products.models import StockPorTalla


class MockShippingCalculator:
    @staticmethod
    def calculate(direccion):
        from decimal import Decimal
        return Decimal("15.00")


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
            raise ValueError("El carrito está vacío.")

        costo_envio = MockShippingCalculator.calculate(datos_envio.get('direccion_envio', ''))

        # 1. Crear Orden
        orden = Orden.objects.create(
            usuario=usuario,
            direccion_envio=datos_envio.get('direccion_envio', ''),
            ciudad=datos_envio.get('ciudad', ''),
            codigo_postal=datos_envio.get('codigo_postal', ''),
            telefono_contacto=datos_envio.get('telefono_contacto', ''),
            costo_envio=costo_envio,
        )

        # 2. Validar stock y crear items atómicamente
        for cart_item in session_cart:
            producto_obj = cart_item['producto']
            talla = cart_item['talla']
            cantidad_req = cart_item['cantidad']

            stock = StockPorTalla.objects.select_for_update().get(
                producto=producto_obj,
                talla=talla
            )

            if not stock.esta_disponible(cantidad_req):
                raise ValueError(
                    f"Stock insuficiente para {producto_obj.nombre} "
                    f"talla {talla}. (Quedan {stock.cantidad})"
                )

            stock.disminuir(cantidad_req)

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
        try:
            carrito_db = Carrito.objects.get(usuario=usuario, estado=Carrito.EstadoCarrito.ACTIVO)
            carrito_db.limpiar()
            carrito_db.estado = Carrito.EstadoCarrito.CONVERTIDO
            carrito_db.save(update_fields=['estado'])
        except Carrito.DoesNotExist:
            pass

        return orden

    @staticmethod
    @transaction.atomic
    def cancelar_orden(orden):
        """Cancela la orden y restablece el stock atómicamente."""
        if orden.estado == Orden.EstadoOrden.CANCELADA:
            return

        # Recuperar stock bloqueando los registros
        for item in orden.items.all():
            stock = StockPorTalla.objects.select_for_update().get(
                producto=item.producto,
                talla=item.talla
            )
            stock.aumentar(item.cantidad)

        orden.cancelar()
