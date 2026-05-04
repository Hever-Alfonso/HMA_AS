from decimal import Decimal
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.test import TestCase

from products.models import Categoria, Marca, Producto, StockPorTalla

from .cart import Cart
from .models import Carrito, ItemCarrito
from .services import CartMergeService


class CartTestMixin:
    def create_product(self, name='Test Product', slug='test-product', price='100.00'):
        category = Categoria.objects.create(nombre=f'{name} Category', slug=f'{slug}-category')
        brand = Marca.objects.create(nombre=f'{name} Brand', slug=f'{slug}-brand')
        product = Producto.objects.create(
            nombre=name,
            slug=slug,
            descripcion='Description',
            precio=Decimal(price),
            marca=brand,
            categoria=category,
        )
        StockPorTalla.objects.create(producto=product, talla='M', cantidad=10)
        return product

    def request_with_session(self):
        session = self.client.session
        return SimpleNamespace(session=session)


class CartSessionTest(CartTestMixin, TestCase):
    def setUp(self):
        self.product = self.create_product()
        self.request = self.request_with_session()
        self.cart = Cart(self.request)

    def test_cart_uses_product_and_size_composite_key(self):
        self.cart.add(self.product, 'M', cantidad=2)

        self.assertIn(f'{self.product.id}:M', self.cart.cart)
        self.assertEqual(len(self.cart), 2)

    def test_agregar_producto_al_carrito_incrementa_cantidad(self):
        self.cart.add(self.product, 'M', cantidad=1)
        self.cart.add(self.product, 'M', cantidad=1)

        item = self.cart.cart[f'{self.product.id}:M']
        self.assertEqual(item['cantidad'], 2)

    def test_cart_update_remove_and_total(self):
        self.cart.add(self.product, 'M', cantidad=2)
        self.cart.update(self.product, 'M', cantidad=3)

        self.assertEqual(len(self.cart), 3)
        self.assertEqual(self.cart.total, Decimal('300.00'))

        self.cart.remove(self.product, 'M')
        self.assertEqual(len(self.cart), 0)


class CartMergeServiceTest(CartTestMixin, TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='buyer',
            email='buyer@example.com',
            password='pass12345',
        )
        self.product = self.create_product()
        self.other_product = self.create_product('Other Product', 'other-product', '50.00')
        self.request = self.request_with_session()

    def test_db_cart_has_precedence_when_session_conflicts(self):
        db_cart = Carrito.objects.create(usuario=self.user)
        ItemCarrito.objects.create(
            carrito=db_cart,
            producto=self.product,
            talla='M',
            cantidad=5,
            precio_unitario=self.product.precio,
        )
        session_cart = Cart(self.request)
        session_cart.add(self.product, 'M', cantidad=2)
        session_cart.add(self.other_product, 'M', cantidad=1)

        CartMergeService.merge_session_into_db(self.request, self.user)

        db_cart.refresh_from_db()
        items = {
            f'{item.producto_id}:{item.talla}': item.cantidad
            for item in db_cart.items.all()
        }
        self.assertEqual(items[f'{self.product.id}:M'], 5)
        self.assertEqual(items[f'{self.other_product.id}:M'], 1)

        merged_session = self.request.session[Cart.SESSION_KEY]
        self.assertEqual(merged_session[f'{self.product.id}:M']['cantidad'], 5)
        self.assertEqual(merged_session[f'{self.other_product.id}:M']['cantidad'], 1)
