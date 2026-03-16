from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class SuccessMessageMixin:
    """Agrega mensaje de éxito automáticamente al form_valid"""
    success_message = ""

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response


class AdminRequiredMixin(LoginRequiredMixin):
    """Requiere que el usuario sea administrador"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.rol != 'admin':
            messages.error(request, "No tienes permisos para acceder a esta página.")
            return redirect('core:home')
        return super().dispatch(request, *args, **kwargs)


class OwnerRequiredMixin(UserPassesTestMixin):
    """Solo el dueño del objeto puede acceder"""

    def test_func(self):
        obj = self.get_object()
        return obj.usuario == self.request.user
