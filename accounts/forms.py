from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from .models import Usuario


phone_validator = RegexValidator(
    regex=r'^\d+$',
    message=_("El telefono solo debe contener numeros."),
)


class CustomUserCreationForm(UserCreationForm):
    telefono = forms.CharField(
        required=False,
        max_length=15,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'inputmode': 'numeric',
            'pattern': r'\d*',
        }),
    )

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('username', 'email', 'telefono')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = Usuario.RolUsuario.CLIENTE
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    telefono = forms.CharField(
        required=False,
        max_length=15,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'inputmode': 'numeric',
            'pattern': r'\d*',
        }),
    )

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'telefono', 'rol')
