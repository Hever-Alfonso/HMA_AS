from django.urls import path

from .views import ProductApiDetailView, ProductApiListView

app_name = 'products_api'

urlpatterns = [
    path('products/', ProductApiListView.as_view(), name='product_list'),
    path('products/<slug:slug>/', ProductApiDetailView.as_view(), name='product_detail'),
]
