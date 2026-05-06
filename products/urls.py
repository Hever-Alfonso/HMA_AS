from django.urls import path
from .views import (
    ProductApiDetailView,
    ProductApiListView,
    ProductDetailView,
    ProductListView,
)

app_name = 'products'

urlpatterns = [
    path('api/products/', ProductApiListView.as_view(), name='api_product_list'),
    path('api/products/<slug:slug>/', ProductApiDetailView.as_view(), name='api_product_detail'),
    path('', ProductListView.as_view(), name='product_list'),
    path('category/<slug:category_slug>/', ProductListView.as_view(), name='product_list_by_category'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
]
