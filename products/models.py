from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from decimal import Decimal

from core.models import TimestampMixin, SoftDeleteMixin, ActivableMixin
from core.managers import SoftDeleteManager, ActiveManager


class Categoria(TimestampMixin, models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    descripcion = models.TextField(blank=True)
    imagen_portada = models.ImageField(upload_to='categorias/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = 'Categorías'


class Marca(TimestampMixin, models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Producto(TimestampMixin, SoftDeleteMixin, ActivableMixin, models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    descripcion = models.TextField()
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    marca = models.ForeignKey(
        Marca,
        on_delete=models.PROTECT,
        related_name='productos'
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='productos'
    )
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    objects = SoftDeleteManager()
    activos = ActiveManager()
    all_objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    @property
    def stock_total(self):
        """Calcula stock total sumando todas las tallas"""
        return self.stock_por_talla.aggregate(
            models.Sum('cantidad')
        )['cantidad__sum'] or 0

    @property
    def tiene_stock(self):
        return self.stock_total > 0

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Productos'


class ImagenProducto(models.Model):
    """Modelo separado para manejar múltiples imágenes por producto"""
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='imagenes'
    )
    imagen = models.ImageField(upload_to='productos/%Y/%m/%d/')
    orden = models.PositiveIntegerField(default=0)
    es_principal = models.BooleanField(default=False)

    class Meta:
        ordering = ['orden']
        verbose_name = 'Imagen de Producto'
        verbose_name_plural = 'Imágenes de Productos'

    def __str__(self):
        return f"Imagen {self.orden} de {self.producto.nombre}"


class StockPorTalla(models.Model):
    class Talla(models.TextChoices):
        XS = 'XS', 'Extra Small'
        S = 'S', 'Small'
        M = 'M', 'Medium'
        L = 'L', 'Large'
        XL = 'XL', 'Extra Large'
        XXL = 'XXL', 'Double Extra Large'

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='stock_por_talla'
    )
    talla = models.CharField(max_length=5, choices=Talla.choices)
    cantidad = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['producto', 'talla']
        verbose_name = 'Stock por Talla'
        verbose_name_plural = 'Stock por Tallas'

    def __str__(self):
        return f"{self.producto.nombre} - Talla {self.talla}: {self.cantidad}"

    def aumentar(self, cantidad):
        self.cantidad += cantidad
        self.save(update_fields=['cantidad'])

    def disminuir(self, cantidad):
        if cantidad > self.cantidad:
            raise ValueError(f"Stock insuficiente. Disponible: {self.cantidad}")
        self.cantidad -= cantidad
        self.save(update_fields=['cantidad'])

    def esta_disponible(self, cantidad=1):
        return self.cantidad >= cantidad