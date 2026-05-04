from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView

from products.models import Producto

from .cart import Cart
from .services import CartService


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
        producto_id = request.POST.get("product_id")
        talla = request.POST.get("size_id")
        cantidad = request.POST.get("quantity", 1)
        producto = get_object_or_404(Producto, id=producto_id)

        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError):
            cantidad = 1

        try:
            CartService.add_item(request, producto, talla, cantidad)
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("products:product_detail", slug=producto.slug)

        messages.success(request, "Producto agregado al carrito.")
        return redirect("cart:detail")


class CartUpdateView(View):
    def post(self, request, *args, **kwargs):
        producto_id = request.POST.get("product_id")
        talla = request.POST.get("size_id")
        cantidad = request.POST.get("quantity", 1)
        producto = get_object_or_404(Producto, id=producto_id)

        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError):
            cantidad = 1

        try:
            CartService.update_item(request, producto, talla, cantidad)
        except ValueError as exc:
            messages.error(request, str(exc))

        return redirect("cart:detail")


class CartRemoveView(View):
    def post(self, request, *args, **kwargs):
        producto_id = request.POST.get("product_id")
        talla = request.POST.get("size_id")
        producto = get_object_or_404(Producto, id=producto_id)

        CartService.remove_item(request, producto, talla)
        return redirect("cart:detail")
