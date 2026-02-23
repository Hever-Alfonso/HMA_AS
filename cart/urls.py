from django.urls import path
from .views import CartDetailView, CartAddView, CartUpdateView, CartRemoveView

app_name = "cart"

urlpatterns = [
    path("", CartDetailView.as_view(), name="detail"),
    path("add/", CartAddView.as_view(), name="add"),
    path("update/", CartUpdateView.as_view(), name="update"),
    path("remove/", CartRemoveView.as_view(), name="remove"),
]