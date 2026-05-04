from django.db.models import Q, Sum, Min, Max

from .models import Producto, Categoria, Marca


class ProductoRepository:
    """Repositorio para acceso a datos de productos"""

    SORT_FIELDS = {
        'price_asc': 'precio',
        'price_desc': '-precio',
        'newest': '-id',
        None: '-id',
        '': '-id',
    }

    def obtener_por_id(self, producto_id):
        return Producto.objects.select_related(
            'marca', 'categoria'
        ).prefetch_related(
            'imagenes',
            'stock_por_talla'
        ).get(id=producto_id)

    def buscar(
        self,
        query=None,
        categoria=None,
        marca=None,
        precio_min=None,
        precio_max=None,
        talla=None,
        sort=None,
    ):
        queryset = Producto.activos.select_related(
            'marca', 'categoria'
        ).prefetch_related(
            'stock_por_talla', 'imagenes'
        )

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
        if talla:
            queryset = queryset.filter(
                stock_por_talla__talla=talla,
                stock_por_talla__cantidad__gt=0,
            ).distinct()

        return queryset.order_by(self.SORT_FIELDS.get(sort, '-id'))

    def obtener_activo_por_slug(self, slug):
        return Producto.activos.select_related(
            'marca', 'categoria'
        ).prefetch_related(
            'stock_por_talla', 'imagenes'
        ).get(slug=slug)

    def obtener_con_stock(self, talla=None):
        queryset = Producto.activos.select_related(
            'marca', 'categoria'
        ).prefetch_related(
            'stock_por_talla', 'imagenes'
        ).filter(
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
