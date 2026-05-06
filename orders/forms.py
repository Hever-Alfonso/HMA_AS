from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


solo_numeros_validator = RegexValidator(
    regex=r"^\d+$",
    message=_("Este campo solo permite números."),
)

solo_texto_ciudad_validator = RegexValidator(
    regex=r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s'-]+$",
    message=_("La ciudad solo puede contener letras y espacios."),
)

required_message = _("Este campo es obligatorio.")


class CheckoutForm(forms.Form):
    direccion_envio = forms.CharField(
        required=True,
        error_messages={"required": required_message},
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    ciudad = forms.CharField(
        required=True,
        max_length=100,
        error_messages={"required": required_message},
        validators=[solo_texto_ciudad_validator],
    )
    codigo_postal = forms.CharField(
        required=True,
        max_length=10,
        error_messages={"required": required_message},
        validators=[solo_numeros_validator],
    )
    telefono_contacto = forms.CharField(
        required=True,
        max_length=15,
        error_messages={"required": required_message},
        validators=[solo_numeros_validator],
    )
