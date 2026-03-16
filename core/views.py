from django.views.generic import TemplateView
from products.models import Producto

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Producto.objects.filter(activo=True)[:3]
        return context

class AboutView(TemplateView):
    template_name = 'core/about.html'