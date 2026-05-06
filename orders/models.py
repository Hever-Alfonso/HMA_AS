from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimestampMixin
from products.models import Producto, StockPorTalla


class Orden(TimestampMixin, models.Model):
    class EstadoOrden(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        CONFIRMADA = 'confirmada', 'Confirmada'
        PAGADA = 'pagada', 'Pagada'
        ENVIADA = 'enviada', 'Enviada'
        ENTREGADA = 'entregada', 'Entregada'
        CANCELADA = 'cancelada', 'Cancelada'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='ordenes'
    )
    fecha_orden = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20,
        choices=EstadoOrden.choices,
        default=EstadoOrden.PENDIENTE
    )
    monto_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        editable=False,
        validators=[MinValueValidator(0)]
    )

    # Información de envío
    direccion_envio = models.TextField()
    ciudad = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    telefono_contacto = models.CharField(max_length=15, blank=True)
    costo_envio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    numero_rastreo = models.CharField(max_length=100, blank=True, null=True)

    # Timestamps de estados
    fecha_pago = models.DateTimeField(null=True, blank=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Orden'
        verbose_name_plural = 'Órdenes'
        indexes = [
            models.Index(fields=['usuario', 'estado'], name='orden_usuario_estado_idx'),
        ]

    def __str__(self):
        return f"Orden #{self.id} - {self.usuario.email}"

    def clean(self):
        errors = {}
        if not self.direccion_envio:
            errors["direccion_envio"] = _("La dirección de envío es obligatoria.")
        if not self.ciudad:
            errors["ciudad"] = _("La ciudad es obligatoria.")
        if not self.codigo_postal:
            errors["codigo_postal"] = _("El código postal es obligatorio.")
        if not self.telefono_contacto:
            errors["telefono_contacto"] = _("El teléfono de contacto es obligatorio.")
        if self.estado not in self.EstadoOrden.values:
            errors["estado"] = _("El estado de la orden no es válido.")
        if errors:
            raise ValidationError(errors)

    def calcular_total(self):
        total = sum(item.subtotal for item in self.items.all()) + self.costo_envio
        self.monto_total = total
        self.save(update_fields=['monto_total'])
        return total

    def marcar_como_pagada(self):
        from django.utils import timezone
        self.estado = self.EstadoOrden.PAGADA
        self.fecha_pago = timezone.now()
        self.save(update_fields=['estado', 'fecha_pago'])

    def cancelar(self):
        if self.estado in [self.EstadoOrden.ENVIADA, self.EstadoOrden.ENTREGADA]:
            raise ValueError(_("No se puede cancelar una orden ya enviada o entregada"))
        self.estado = self.EstadoOrden.CANCELADA
        self.save(update_fields=['estado'])


class ItemOrden(models.Model):
    orden = models.ForeignKey(
        Orden,
        on_delete=models.CASCADE,
        related_name='items'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT
    )
    talla = models.CharField(max_length=5, choices=StockPorTalla.Talla.choices)
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta:
        verbose_name = 'Item de Orden'
        verbose_name_plural = 'Items de Orden'

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} ({self.talla})"

    def save(self, *args, **kwargs):
        if self.cantidad <= 0:
            raise ValueError(_("La cantidad debe ser positiva."))
        if self.talla not in StockPorTalla.Talla.values:
            raise ValueError(_("La talla seleccionada no es válida."))
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)
