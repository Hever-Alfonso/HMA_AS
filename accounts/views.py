from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
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

from cart.cart import Cart
from cart.models import Carrito

class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        session_cart = Cart(self.request)
        
        db_cart, _ = Carrito.objects.get_or_create(usuario=user, estado='activo')
        
        for s_item in session_cart:
            db_cart.agregar_item(s_item['producto'], s_item['talla'], s_item['cantidad'])
            
        for d_item in db_cart.items.all():
            session_cart.add(d_item.producto, d_item.talla, cantidad=d_item.cantidad, override_cantidad=True)
            
        messages.success(self.request, "Has iniciado sesión correctamente.")
        return response

from django.contrib.auth import logout
from django.views import View

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
