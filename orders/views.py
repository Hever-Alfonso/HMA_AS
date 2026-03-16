from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from .models import Order


class CheckoutView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, "orders/checkout.html")

    def post(self, request):

        shippingAddress = request.POST.get("direccion_envio")
        city = request.POST.get("ciudad")
        postalCode = request.POST.get("codigo_postal")
        contactPhone = request.POST.get("telefono_contacto")

        order = Order.objects.create(
            userId=request.user,
            shippingAddress=shippingAddress,
            city=city,
            postalCode=postalCode,
            contactPhone=contactPhone
        )

        messages.success(request, "Order created successfully")

        return redirect("orders:order_detail", order_id=order.id)


class OrderDetailView(LoginRequiredMixin, View):

    def get(self, request, order_id):

        order = get_object_or_404(Order, id=order_id, userId=request.user)

        return render(
            request,
            "orders/detalle.html",
            {"orden": order}
        )

def order_pdf(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    template = get_template("orders/order_pdf.html")
    html = template.render({"order": order})

    response = HttpResponse(content_type="application/pdf")

    pisa.CreatePDF(html, dest=response)

    return response