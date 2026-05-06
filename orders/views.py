from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext as _
from .services import OrdenService
from .models import Orden
from .forms import CheckoutForm


class CheckoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = CheckoutForm()
        return render(request, 'orders/checkout.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = CheckoutForm(request.POST)

        if not form.is_valid():
            messages.error(request, _("Por favor corrige los errores del formulario de checkout."))
            return render(request, 'orders/checkout.html', {'form': form}, status=400)

        datos_envio = form.cleaned_data

        try:
            orden = OrdenService.crear_desde_carrito(request.user, request, datos_envio)
            messages.success(
                request,
                _("¡Gracias por tu compra! Tu orden #%(order_id)s ha sido confirmada.")
                % {"order_id": orden.id},
            )
            return redirect('orders:detalle_orden', orden_id=orden.id)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('cart:detail')
        except Exception as e:
            messages.error(request, _("Ocurrió un error inesperado al procesar tu orden."))
            return redirect('cart:detail')


class CancelarOrdenView(LoginRequiredMixin, View):
    def post(self, request, orden_id, *args, **kwargs):
        orden = get_object_or_404(Orden, id=orden_id, usuario=request.user)
        try:
            OrdenService.cancelar_orden(orden)
            messages.success(
                request,
                _("La orden #%(order_id)s ha sido cancelada y el stock restaurado.")
                % {"order_id": orden.id},
            )
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, _("No se pudo cancelar la orden: %(error)s") % {"error": str(e)})
        return redirect('orders:detalle_orden', orden_id=orden.id)


class OrdenDetailView(LoginRequiredMixin, View):
    def get(self, request, orden_id, *args, **kwargs):
        orden = get_object_or_404(Orden, id=orden_id, usuario=request.user)
        return render(request, 'orders/detalle.html', {'orden': orden})
