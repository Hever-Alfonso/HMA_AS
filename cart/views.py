from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

from products.models import Product, StockBySize
from .cart import Cart

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
        product_id = request.POST.get("product_id")
        size = request.POST.get("size")
        quantity = request.POST.get("quantity", 1)

        product = get_object_or_404(Product, id=product_id)

        if not size:
            messages.error(request, "Debes seleccionar una talla.")
            return redirect("products:product_detail", slug=product.slug)

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            quantity = 1

        stock = StockBySize.objects.filter(productId=product, size=size).first()
        available_stock = stock.quantity if stock else 0

        if available_stock <= 0:
            messages.error(request, f"La talla {size} está agotada.")
            return redirect("products:product_detail", slug=product.slug)

        cart.add(productId=product, size=size, quantity=quantity)
        messages.success(request, "Producto agregado al carrito.")
        return redirect("cart:detail")

class CartUpdateView(View):
    def post(self, request, *args, **kwargs):
        cart = Cart(request)
        product_id = request.POST.get("product_id")
        size = request.POST.get("size")
        quantity = request.POST.get("quantity", 1)

        product = get_object_or_404(Product, id=product_id)

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            quantity = 1

        if quantity <= 0:
            cart.remove(productId=product, size=size)
            return redirect("cart:detail")

        stock = StockBySize.objects.filter(productId=product, size=size).first()
        available_stock = stock.quantity if stock else 0

        if quantity > available_stock:
            messages.error(request, f"No hay suficiente stock para la talla {size}.")
            return redirect("cart:detail")

        cart.update(productId=product, size=size, quantity=quantity)
        return redirect("cart:detail")

class CartRemoveView(View):
    def post(self, request, *args, **kwargs):
        cart = Cart(request)
        product_id = request.POST.get("product_id")
        size = request.POST.get("size")

        product = get_object_or_404(Product, id=product_id)
        cart.remove(productId=product, size=size)
        return redirect("cart:detail")