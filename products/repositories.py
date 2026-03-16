from django.db.models import Q, Sum, Min, Max

from .models import Producto, Categoria, Marca


class ProductoRepository:
    """Repositorio para acceso a datos de productos"""

    def obtener_por_id(self, producto_id):
        return Producto.objects.select_related(
            'marca', 'categoria'
        ).prefetch_related(
            'imagenes',
            'stock_por_talla'
        ).get(id=producto_id)

    def buscar(self, query=None, categoria=None, marca=None, precio_min=None, precio_max=None):
        queryset = Producto.activos.all()

        if query:
            queryset = queryset.filter(
                Q(nombre__icontains=query) |
                Q(descripcion__icontains=query)
            )
        if categoria:
            queryset = queryset.filter(categoria__slug=categoria)
        if marca:
            queryset = queryset.filter(marca__slug=marca)
        if precio_min:
            queryset = queryset.filter(precio__gte=precio_min)
        if precio_max:
            queryset = queryset.filter(precio__lte=precio_max)

        return queryset.select_related('marca', 'categoria')

    def obtener_con_stock(self, talla=None):
        queryset = Producto.activos.filter(
            stock_por_talla__cantidad__gt=0
        )
        if talla:
            queryset = queryset.filter(stock_por_talla__talla=talla)
        return queryset.distinct()

    def obtener_mas_vendidos(self, limit=10):
        return Producto.activos.annotate(
            total_vendido=Sum('itemorden__cantidad')
        ).order_by('-total_vendido')[:limit]

    def obtener_rango_precios(self):
        return Producto.objects.aggregate(Min('precio'), Max('precio'))
