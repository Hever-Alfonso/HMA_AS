from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    # Campos base heredados (username, email, password, first_name, last_name, etc.)
    telefono = models.CharField(max_length=15, blank=True)
    
    class RolUsuario(models.TextChoices):
        CLIENTE = 'cliente', 'Cliente'
        ADMIN = 'admin', 'Administrador'
    
    rol = models.CharField(
        max_length=20,
        choices=RolUsuario.choices,
        default=RolUsuario.CLIENTE
    )

    def __str__(self):
        return self.username
        
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
