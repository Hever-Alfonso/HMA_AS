from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

from products.models import Producto, StockPorTalla
from .cart import Cart
from .models import Carrito

class CartDetailView(TemplateView):
    template_name = "cart/cart_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        context["cart_items"] = list(cart)
        context["cart_total"] = cart.total
        return context

class CartAddView(View):
    def post(self, request, *args, **kwargs):
        cart = Cart(request)
        producto_id = request.POST.get("product_id")
        talla = request.POST.get("size_id")
        cantidad = request.POST.get("quantity", 1)

        producto = get_object_or_404(Producto, id=producto_id)

        if not talla:
            messages.error(request, "Debes seleccionar una talla.")
            return redirect("products:product_detail", slug=producto.slug)

        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError):
            cantidad = 1

        stock = StockPorTalla.objects.filter(producto=producto, talla=talla).first()
        available_stock = stock.cantidad if stock else 0

        if available_stock <= 0:
            messages.error(request, f"La talla {talla} está agotada.")
            return redirect("products:product_detail", slug=producto.slug)

        cart.add(producto=producto, talla=talla, cantidad=cantidad)
        messages.success(request, "Producto agregado al carrito.")
        return redirect("cart:detail")

class CartUpdateView(View):
    def post(self, request, *args, **kwargs):
        cart = Cart(request)
        producto_id = request.POST.get("product_id")
        talla = request.POST.get("size_id")
        cantidad = request.POST.get("quantity", 1)

        producto = get_object_or_404(Producto, id=producto_id)

        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError):
            cantidad = 1

        if cantidad <= 0:
            cart.remove(producto=producto, talla=talla)
            return redirect("cart:detail")

        stock = StockPorTalla.objects.filter(producto=producto, talla=talla).first()
        available_stock = stock.cantidad if stock else 0

        if cantidad > available_stock:
            messages.error(request, f"No hay suficiente stock para la talla {talla}.")
            return redirect("cart:detail")

        cart.update(producto=producto, talla=talla, cantidad=cantidad)
        return redirect("cart:detail")

class CartRemoveView(View):
    def post(self, request, *args, **kwargs):
        cart = Cart(request)
        producto_id = request.POST.get("product_id")
        talla = request.POST.get("size_id")

        producto = get_object_or_404(Producto, id=producto_id)
        cart.remove(producto=producto, talla=talla)
        return redirect("cart:detail")