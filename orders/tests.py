from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
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


class OrderPermissionTest(OrderTestMixin, TestCase):
    def test_user_cannot_access_another_users_order(self):
        owner = self.create_user('owner')
        intruder = self.create_user('intruder')
        order = Orden.objects.create(usuario=owner, **self.valid_checkout_data())
        self.client.force_login(intruder)

        response = self.client.get(reverse('orders:detalle_orden', args=[order.id]))

        self.assertEqual(response.status_code, 404)
