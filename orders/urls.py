from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('<int:orden_id>/', views.OrdenDetailView.as_view(), name='detalle_orden'),
    path('<int:orden_id>/cancelar/', views.CancelarOrdenView.as_view(), name='cancelar'),
]
