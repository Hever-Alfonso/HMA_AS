from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .services import CartMergeService


@receiver(user_logged_in)
def merge_cart_after_login(sender, request, user, **kwargs):
    """Ejecuta el merge del carrito cuando el usuario inicia sesión."""
    CartMergeService.merge_session_into_db(request, user)
