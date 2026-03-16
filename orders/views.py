from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .services import OrdenService
from .models import Orden


class CheckoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'orders/checkout.html')

    def post(self, request, *args, **kwargs):
        datos_envio = {
            'direccion_envio': request.POST.get('direccion_envio', ''),
            'ciudad': request.POST.get('ciudad', ''),
            'codigo_postal': request.POST.get('codigo_postal', ''),
            'telefono_contacto': request.POST.get('telefono_contacto', ''),
        }

        try:
            orden = OrdenService.crear_desde_carrito(request.user, request, datos_envio)
            messages.success(request, f"¡Gracias por tu compra! Tu orden #{orden.id} ha sido confirmada.")
            return redirect('orders:detalle_orden', orden_id=orden.id)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('cart:detail')
        except Exception as e:
            messages.error(request, "Ocurrió un error inesperado al procesar tu orden.")
            return redirect('cart:detail')


class CancelarOrdenView(LoginRequiredMixin, View):
    def post(self, request, orden_id, *args, **kwargs):
        orden = get_object_or_404(Orden, id=orden_id, usuario=request.user)
        try:
            OrdenService.cancelar_orden(orden)
            messages.success(request, f"La orden #{orden.id} ha sido cancelada y el stock restaurado.")
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"No se pudo cancelar la orden: {str(e)}")
        return redirect('orders:detalle_orden', orden_id=orden.id)


class OrdenDetailView(LoginRequiredMixin, View):
    def get(self, request, orden_id, *args, **kwargs):
        orden = get_object_or_404(Orden, id=orden_id, usuario=request.user)
        return render(request, 'orders/detalle.html', {'orden': orden})
