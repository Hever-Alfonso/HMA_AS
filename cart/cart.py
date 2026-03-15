from decimal import Decimal
from django.conf import settings
from products.models import Producto

class Cart:
    SESSION_KEY = "cart"

    def __init__(self, request):
        self.request = request
        self.session = request.session
        cart = self.session.get(self.SESSION_KEY)
        if not cart:
            cart = self.session[self.SESSION_KEY] = {}
        self.cart = cart

    def _make_key(self, producto_id, talla):
        return f"{producto_id}:{talla}"

    def add(self, producto, talla, cantidad=1, override_cantidad=False):
        producto_id = str(producto.id)
        key = self._make_key(producto_id, talla)

        if key not in self.cart:
            self.cart[key] = {
                "producto_id": producto_id,
                "talla": talla,
                "cantidad": 0,
                "precio_unitario": str(producto.precio),
            }

        if override_cantidad:
            self.cart[key]["cantidad"] = cantidad
        else:
            self.cart[key]["cantidad"] += cantidad

        if self.cart[key]["cantidad"] <= 0:
            del self.cart[key]

        self.save()

    def remove(self, producto, talla):
        key = self._make_key(str(producto.id), talla)
        if key in self.cart:
            del self.cart[key]
            self.save()

    def update(self, producto, talla, cantidad):
        self.add(producto, talla, cantidad=cantidad, override_cantidad=True)

    def save(self):
        self.session[self.SESSION_KEY] = self.cart
        self.session.modified = True

    def clear(self):
        self.session[self.SESSION_KEY] = {}
        self.session.modified = True

    def __iter__(self):
        keys = list(self.cart.keys())
        producto_ids = {item["producto_id"] for item in self.cart.values()}
        productos = {str(p.id): p for p in Producto.objects.filter(id__in=producto_ids)}

        for key in keys:
            item = self.cart[key]
            producto = productos.get(item["producto_id"])

            if not producto:
                continue

            precio = Decimal(item["precio_unitario"])
            cantidad = int(item["cantidad"])
            subtotal = precio * cantidad

            yield {
                "key": key,
                "producto": producto,
                "talla": item["talla"],
                "cantidad": cantidad,
                "precio_unitario": precio,
                "subtotal": subtotal,
            }

    def __len__(self):
        return sum(int(item["cantidad"]) for item in self.cart.values())

    @property
    def total(self):
        total = Decimal("0.00")
        for item in self:
            total += item["subtotal"]
        return total