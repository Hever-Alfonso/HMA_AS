from decimal import Decimal
from django.conf import settings
from products.models import Product

class Cart:
    SESSION_KEY = "cart"

    def __init__(self, request):
        self.request = request
        self.session = request.session
        cart = self.session.get(self.SESSION_KEY)
        if not cart:
            cart = self.session[self.SESSION_KEY] = {}
        self.cart = cart

    def _make_key(self, product_id, size):
        return f"{product_id}:{size}"

    def add(self, product, size, quantity=1, override_quantity=False):
        product_id = str(product.id)
        key = self._make_key(product_id, size)

        if key not in self.cart:
            self.cart[key] = {
                "product_id": product_id,
                "size": size,
                "quantity": 0,
                "price": str(product.price),
            }

        if override_quantity:
            self.cart[key]["quantity"] = quantity
        else:
            self.cart[key]["quantity"] += quantity

        if self.cart[key]["quantity"] <= 0:
            del self.cart[key]

        self.save()

    def remove(self, product, size):
        key = self._make_key(str(product.id), size)
        if key in self.cart:
            del self.cart[key]
            self.save()

    def update(self, product, size, quantity):
        self.add(product, size, quantity=quantity, override_quantity=True)

    def save(self):
        self.session[self.SESSION_KEY] = self.cart
        self.session.modified = True

    def clear(self):
        self.session[self.SESSION_KEY] = {}
        self.session.modified = True

    def __iter__(self):
        keys = list(self.cart.keys())
        product_ids = {item["product_id"] for item in self.cart.values()}
        products = {str(p.id): p for p in Product.objects.filter(id__in=product_ids)}

        for key in keys:
            item = self.cart[key]
            product = products.get(item["product_id"])

            if not product:
                continue

            price = Decimal(item["price"])
            quantity = int(item["quantity"])
            subtotal = price * quantity

            yield {
                "key": key,
                "product": product,
                "size": item["size"],
                "quantity": quantity,
                "unit_price": price,
                "subtotal": subtotal,
            }

    def __len__(self):
        return sum(int(item["quantity"]) for item in self.cart.values())

    @property
    def total(self):
        total = Decimal("0.00")
        for item in self:
            total += item["subtotal"]
        return total