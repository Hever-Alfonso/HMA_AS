from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView

from .forms import CustomUserCreationForm


class RegistroView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'usuarios/registro.html'
    success_url = reverse_lazy('core:home')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Registro exitoso. ¡Bienvenido a UNLABELED!")
        return redirect(self.success_url)


class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Has iniciado sesión correctamente.")
        return response


class CustomLogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, "Has cerrado sesión.")
        return render(request, 'usuarios/logout.html')

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, "Has cerrado sesión.")
        return render(request, 'usuarios/logout.html')


class PerfilView(LoginRequiredMixin, TemplateView):
    template_name = 'usuarios/perfil.html'
