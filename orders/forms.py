from django import forms
from django.core.validators import RegexValidator


solo_numeros_validator = RegexValidator(
    regex=r"^\d+$",
    message="Este campo solo permite numeros.",
)

solo_texto_ciudad_validator = RegexValidator(
    regex=r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s'-]+$",
    message="La ciudad solo puede contener letras y espacios.",
)


class CheckoutForm(forms.Form):
    direccion_envio = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    ciudad = forms.CharField(
        required=True,
        max_length=100,
        validators=[solo_texto_ciudad_validator],
    )
    codigo_postal = forms.CharField(
        required=True,
        max_length=10,
        validators=[solo_numeros_validator],
    )
    telefono_contacto = forms.CharField(
        required=True,
        max_length=15,
        validators=[solo_numeros_validator],
    )
