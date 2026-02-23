from django.views.generic import TemplateView
from products.models import Product

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.all()[:3]
        return context

class AboutView(TemplateView):
    template_name = 'core/about.html'