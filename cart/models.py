from django.db import models
from django.conf import settings
from products.models import Producto, StockPorTalla
from core.models import TimestampMixin


class Carrito(TimestampMixin, models.Model):
    class EstadoCarrito(models.TextChoices):
        ACTIVO = 'activo', 'Activo'
        CONVERTIDO = 'convertido', 'Convertido a Orden'
        ABANDONADO = 'abandonado', 'Abandonado'

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carrito'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=EstadoCarrito.choices,
        default=EstadoCarrito.ACTIVO
    )

    class Meta:
        verbose_name_plural = 'Carritos'

    def __str__(self):
        if self.usuario:
            return f"Carrito de {self.usuario.email}"
        return f"Carrito de sesión {self.session_key}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def cantidad_items(self):
        return self.items.aggregate(
            models.Sum('cantidad')
        )['cantidad__sum'] or 0

    def agregar_item(self, producto_obj, talla, cantidad=1):
        item, created = ItemCarrito.objects.get_or_create(
            carrito=self,
            producto=producto_obj,
            talla=talla,
            defaults={'cantidad': cantidad}
        )
        if not created:
            item.cantidad += cantidad
            item.save()

    def remover_item(self, producto_obj, talla):
        ItemCarrito.objects.filter(carrito=self, producto=producto_obj, talla=talla).delete()

    def actualizar_item(self, producto_obj, talla, cantidad):
        item = ItemCarrito.objects.filter(carrito=self, producto=producto_obj, talla=talla).first()
        if item:
            item.cantidad = cantidad
            item.save()

    def limpiar(self):
        self.items.all().delete()


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(
        Carrito,
        on_delete=models.CASCADE,
        related_name='items'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE
    )
    talla = models.CharField(max_length=5, choices=StockPorTalla.Talla.choices)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ['carrito', 'producto', 'talla']
        verbose_name = 'Item de Carrito'
        verbose_name_plural = 'Items de Carrito'

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} ({self.talla})"

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad

    def save(self, *args, **kwargs):
        if not self.precio_unitario:
            self.precio_unitario = self.producto.precio
        super().save(*args, **kwargs)
