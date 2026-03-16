from django.contrib import admin
from .models import Producto, StockPorTalla, Categoria, Marca, ImagenProducto


class StockPorTallaInline(admin.TabularInline):
    model = StockPorTalla
    extra = 1


class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'marca', 'categoria', 'precio', 'activo', 'stock_total')
    list_filter = ('marca', 'categoria', 'activo')
    search_fields = ('nombre', 'descripcion', 'marca__nombre', 'categoria__nombre')
    prepopulated_fields = {'slug': ('nombre',)}
    exclude = ('is_deleted', 'deleted_at')
    inlines = [StockPorTallaInline, ImagenProductoInline]

    def stock_total(self, obj):
        return obj.stock_total
    stock_total.short_description = 'Stock Total'


@admin.register(StockPorTalla)
class StockPorTallaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'talla', 'cantidad')
    list_filter = ('talla',)
    search_fields = ('producto__nombre',)