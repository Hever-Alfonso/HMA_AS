from django.contrib import admin
from .models import Orden, ItemOrden


class ItemOrdenInline(admin.TabularInline):
    model = ItemOrden
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha_orden', 'estado', 'monto_total', 'ciudad')
    list_filter = ('estado', 'fecha_orden')
    search_fields = ('id', 'usuario__username', 'usuario__email')
    readonly_fields = ('monto_total', 'fecha_pago', 'fecha_envio', 'fecha_entrega')
    inlines = [ItemOrdenInline]


@admin.register(ItemOrden)
class ItemOrdenAdmin(admin.ModelAdmin):
    list_display = ('orden', 'producto', 'talla', 'cantidad', 'precio_unitario', 'subtotal')
    readonly_fields = ('subtotal',)
