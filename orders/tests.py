from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from cart.cart import Cart
from products.models import Categoria, Marca, Producto, StockPorTalla

from .models import Orden


class OrderTestMixin:
    def create_user(self, username='buyer'):
        return get_user_model().objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='pass12345',
        )

    def create_product(self, stock=5):
        category = Categoria.objects.create(nombre='Order Category', slug='order-category')
        brand = Marca.objects.create(nombre='Order Brand', slug='order-brand')
        product = Producto.objects.create(
            nombre='Order Product',
            slug='order-product',
            descripcion='Description',
            precio=Decimal('100.00'),
            marca=brand,
            categoria=category,
        )
        StockPorTalla.objects.create(producto=product, talla='M', cantidad=stock)
        return product

    def valid_checkout_data(self):
        return {
            'direccion_envio': 'Calle 1 #2-3',
            'ciudad': 'Medellin',
            'codigo_postal': '050001',
            'telefono_contacto': '3001234567',
        }


@override_settings(SHIPPING_RATE_PROVIDER='fixed', FIXED_SHIPPING_RATE='15000.00')
class CheckoutIntegrationTest(OrderTestMixin, TestCase):
    def setUp(self):
        self.user = self.create_user()
        self.client.force_login(self.user)
        self.product = self.create_product(stock=1)

    def test_checkout_rejects_empty_cart(self):
        response = self.client.post(reverse('orders:checkout'), self.valid_checkout_data())

        self.assertRedirects(response, reverse('cart:detail'))
        self.assertEqual(Orden.objects.count(), 0)

    def test_checkout_rejects_insufficient_stock(self):
        session = self.client.session
        session[Cart.SESSION_KEY] = {
            f'{self.product.id}:M': {
                'producto_id': str(self.product.id),
                'talla': 'M',
                'cantidad': 2,
                'precio_unitario': str(self.product.precio),
            }
        }
        session.save()

        response = self.client.post(reverse('orders:checkout'), self.valid_checkout_data())

        self.assertRedirects(response, reverse('cart:detail'))
        self.assertEqual(Orden.objects.count(), 0)

    def test_checkout_creates_paid_order_with_fixed_shipping_provider(self):
        session = self.client.session
        session[Cart.SESSION_KEY] = {
            f'{self.product.id}:M': {
                'producto_id': str(self.product.id),
                'talla': 'M',
                'cantidad': 1,
                'precio_unitario': str(self.product.precio),
            }
        }
        session.save()

        response = self.client.post(reverse('orders:checkout'), self.valid_checkout_data())

        order = Orden.objects.get()
        self.assertRedirects(response, reverse('orders:detalle_orden', args=[order.id]))
        self.assertEqual(order.estado, Orden.EstadoOrden.PAGADA)
        self.assertEqual(order.costo_envio, Decimal('15000.00'))
        self.assertEqual(order.monto_total, Decimal('15100.00'))


class ShippingRateProviderTest(OrderTestMixin, TestCase):
    @override_settings(
        SHIPPING_RATE_PROVIDER='external',
        BASE_SHIPPING_USD='4.00',
        EXCHANGE_RATE_API_URL='https://example.test/latest/USD',
    )
    def test_external_provider_consumes_exchange_rate_api(self):
        from unittest.mock import patch

        from orders.shipping import ShippingRateProviderFactory

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return False

            def read(self):
                return b'{"rates": {"COP": 4000}}'

        with patch('orders.shipping.urlopen', return_value=FakeResponse()) as urlopen_mock:
            provider = ShippingRateProviderFactory.create()
            cost = provider.calculate(self.valid_checkout_data())

        urlopen_mock.assert_called_once()
        self.assertEqual(cost, Decimal('16000.00'))


class OrderPermissionTest(OrderTestMixin, TestCase):
    def test_user_cannot_access_another_users_order(self):
        owner = self.create_user('owner')
        intruder = self.create_user('intruder')
        order = Orden.objects.create(usuario=owner, **self.valid_checkout_data())
        self.client.force_login(intruder)

        response = self.client.get(reverse('orders:detalle_orden', args=[order.id]))

        self.assertEqual(response.status_code, 404)
