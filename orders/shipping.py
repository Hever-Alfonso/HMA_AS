from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import json
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from django.conf import settings


class ShippingRateProvider(ABC):
    """Abstraccion para calcular el costo de envio de una orden."""

    @abstractmethod
    def calculate(self, shipping_data):
        raise NotImplementedError


class FixedShippingRateProvider(ShippingRateProvider):
    """Proveedor local para entornos sin Internet o como respaldo."""

    def __init__(self, amount=None):
        self.amount = Decimal(str(amount or getattr(settings, "FIXED_SHIPPING_RATE", "15000.00")))

    def calculate(self, shipping_data):
        return self.amount


class ExternalExchangeRateShippingRateProvider(ShippingRateProvider):
    """
    Calcula el envio consumiendo un API externo de tasas de cambio.

    La tarifa base esta en USD y se convierte a COP con la respuesta de
    open.er-api.com. Si el servicio no responde, usa el proveedor fijo.
    """

    def __init__(self, fallback=None):
        self.api_url = getattr(settings, "EXCHANGE_RATE_API_URL", "https://open.er-api.com/v6/latest/USD")
        self.base_amount_usd = Decimal(str(getattr(settings, "BASE_SHIPPING_USD", "4.00")))
        self.timeout = getattr(settings, "SHIPPING_API_TIMEOUT", 3)
        self.fallback = fallback or FixedShippingRateProvider()

    def calculate(self, shipping_data):
        try:
            exchange_rate = self._fetch_cop_rate()
        except (HTTPError, URLError, TimeoutError, ValueError, KeyError, InvalidOperation, json.JSONDecodeError):
            return self.fallback.calculate(shipping_data)

        amount = self.base_amount_usd * exchange_rate
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _fetch_cop_rate(self):
        with urlopen(self.api_url, timeout=self.timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))

        rate = Decimal(str(payload["rates"]["COP"]))
        if rate <= 0:
            raise ValueError("La tasa COP recibida no es valida.")
        return rate


class ShippingRateProviderFactory:
    @staticmethod
    def create():
        provider_name = getattr(settings, "SHIPPING_RATE_PROVIDER", "external").lower()
        providers = {
            "external": ExternalExchangeRateShippingRateProvider,
            "fixed": FixedShippingRateProvider,
        }
        provider_class = providers.get(provider_name, ExternalExchangeRateShippingRateProvider)
        return provider_class()
