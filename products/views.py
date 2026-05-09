from django.db.models import Case, IntegerField, Value, When
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import DetailView, ListView

from .constants import SIZE_ORDER
from .api_serializers import ProductApiSerializer
from .models import Categoria, Producto, StockPorTalla
from .repositories import ProductoRepository


class ProductListView(ListView):
    model = Producto
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        repository = ProductoRepository()
        self.categoria = None
        category_slug = self.kwargs.get('category_slug') or self.request.GET.get('category')

        if category_slug:
            self.categoria = get_object_or_404(Categoria, slug=category_slug)

        return repository.buscar(
            query=self.request.GET.get('q'),
            categoria=category_slug,
            precio_min=self.request.GET.get('min_price'),
            precio_max=self.request.GET.get('max_price'),
            talla=self.request.GET.get('size'),
            sort=self.request.GET.get('sort'),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # All categories for the filter sidebar
        context['categories'] = Categoria.objects.all()
        available_sizes = StockPorTalla.objects.values_list('talla', flat=True).distinct()
        context['sizes'] = [
            size for size in SIZE_ORDER
            if size in set(available_sizes)
        ]
        
        context['current_category_obj'] = self.categoria
        context['current_sort'] = self.request.GET.get('sort', 'newest')
        context['current_min_price'] = self.request.GET.get('min_price', '')
        context['current_max_price'] = self.request.GET.get('max_price', '')
        context['current_size'] = self.request.GET.get('size', '')
        
        return context

class ProductDetailView(DetailView):
    model = Producto
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Producto.activos.select_related(
            'marca', 'categoria'
        ).prefetch_related(
            'stock_por_talla', 'imagenes'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        talla_order_case = Case(
            *[
                When(talla=talla, then=Value(index))
                for index, talla in enumerate(SIZE_ORDER)
            ],
            default=Value(len(SIZE_ORDER)),
            output_field=IntegerField(),
        )
        context['inventory_items'] = product.stock_por_talla.annotate(
            talla_order=talla_order_case
        ).order_by('talla_order', 'id')
        # Related products based on category
        context['related_products'] = Producto.objects.filter(
            categoria=product.categoria, activo=True
        ).select_related('marca', 'categoria').prefetch_related(
            'imagenes', 'stock_por_talla'
        ).exclude(id=product.id)[:4]
        return context


class ProductApiListView(View):
    def get(self, request, *args, **kwargs):
        repository = ProductoRepository()
        serializer = ProductApiSerializer(request)
        products = repository.buscar(
            query=request.GET.get('q'),
            categoria=request.GET.get('category'),
            precio_min=request.GET.get('min_price'),
            precio_max=request.GET.get('max_price'),
            talla=request.GET.get('size'),
            sort=request.GET.get('sort'),
        )

        data = [serializer.serialize_list_item(product) for product in products]
        return JsonResponse({'results': data})


class ProductApiDetailView(View):
    def get(self, request, slug, *args, **kwargs):
        repository = ProductoRepository()
        serializer = ProductApiSerializer(request)
        try:
            product = repository.obtener_activo_por_slug(slug)
        except Producto.DoesNotExist:
            return JsonResponse({'detail': 'Producto no encontrado.'}, status=404)

        return JsonResponse(serializer.serialize_detail(product))
