from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q, Case, When, Value, IntegerField
from .models import Producto, StockPorTalla, Categoria, Marca


TALLA_ORDEN = ['XS', 'S', 'M', 'L', 'XL', 'XXL']

class ProductListView(ListView):
    model = Producto
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Producto.objects.filter(activo=True)
        self.categoria = None
        
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            self.categoria = get_object_or_404(Categoria, slug=category_slug)
            queryset = queryset.filter(categoria=self.categoria)
        
        # Keyword Search
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(nombre__icontains=query) | 
                Q(descripcion__icontains=query)
            )

        # Price Filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(precio__gte=min_price)
        if max_price:
            queryset = queryset.filter(precio__lte=max_price)

        # Size Filter
        size_name = self.request.GET.get('size')
        if size_name:
            queryset = queryset.filter(
                stock_por_talla__talla=size_name,
                stock_por_talla__cantidad__gt=0
            ).distinct()

        # Sorting
        sort = self.request.GET.get('sort')
        if sort == 'price_asc':
            queryset = queryset.order_by('precio')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-precio')
        else:
            queryset = queryset.order_by('-id')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # All categories for the filter sidebar
        context['categories'] = Categoria.objects.all()
        context['sizes'] = StockPorTalla.objects.values_list('talla', flat=True).distinct()
        
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
        return Producto.objects.filter(activo=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        talla_order_case = Case(
            *[
                When(talla=talla, then=Value(index))
                for index, talla in enumerate(TALLA_ORDEN)
            ],
            default=Value(len(TALLA_ORDEN)),
            output_field=IntegerField(),
        )
        context['inventory_items'] = product.stock_por_talla.annotate(
            talla_order=talla_order_case
        ).order_by('talla_order', 'id')
        # Related products based on category
        context['related_products'] = Producto.objects.filter(
            categoria=product.categoria, activo=True
        ).exclude(id=product.id)[:4]
        return context