from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse

from .models import Categoria, Marca, Producto, StockPorTalla
from .repositories import ProductoRepository


class ProductTestMixin:
    def create_base_product(self, name='Test Product', slug='test-product', price='100.00', active=True):
        category = Categoria.objects.create(
            nombre=f'{name} Category',
            slug=f'{slug}-category',
        )
        brand = Marca.objects.create(
            nombre=f'{name} Brand',
            slug=f'{slug}-brand',
        )
        product = Producto.objects.create(
            nombre=name,
            slug=slug,
            descripcion=f'{name} description',
            precio=Decimal(price),
            marca=brand,
            categoria=category,
            activo=active,
        )
        return category, brand, product


class ProductModelTest(ProductTestMixin, TestCase):
    def test_invalid_price_fails_validation(self):
        category, brand, _ = self.create_base_product()
        product = Producto(
            nombre='Invalid Product',
            slug='invalid-product',
            descripcion='Invalid',
            precio=Decimal('0.00'),
            marca=brand,
            categoria=category,
        )

        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_slug_is_created_automatically(self):
        category = Categoria.objects.create(nombre='Auto Category')
        brand = Marca.objects.create(nombre='Auto Brand')
        product = Producto.objects.create(
            nombre='Auto Slug Product',
            descripcion='Auto slug',
            precio=Decimal('25.00'),
            marca=brand,
            categoria=category,
        )

        self.assertEqual(category.slug, 'auto-category')
        self.assertEqual(brand.slug, 'auto-brand')
        self.assertEqual(product.slug, 'auto-slug-product')

    def test_stock_available_and_stock_mutations(self):
        _, _, product = self.create_base_product()
        stock = StockPorTalla.objects.create(producto=product, talla='M', cantidad=3)

        self.assertTrue(stock.esta_disponible(2))
        stock.disminuir(2)
        stock.refresh_from_db()
        self.assertEqual(stock.cantidad, 1)
        stock.aumentar(4)
        stock.refresh_from_db()
        self.assertEqual(stock.cantidad, 5)

    def test_stock_rejects_invalid_mutation_amounts(self):
        _, _, product = self.create_base_product()
        stock = StockPorTalla.objects.create(producto=product, talla='S', cantidad=1)

        with self.assertRaises(ValueError):
            stock.disminuir(0)
        with self.assertRaises(ValueError):
            stock.aumentar(0)
        with self.assertRaises(ValueError):
            stock.disminuir(2)


class ProductCatalogTest(ProductTestMixin, TestCase):
    def setUp(self):
        self.category, self.brand, self.product = self.create_base_product()
        StockPorTalla.objects.create(producto=self.product, talla='M', cantidad=5)

    def test_catalog_view(self):
        response = self.client.get(reverse('products:product_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.nombre)

    def test_catalog_combined_filters(self):
        other_category, other_brand, other_product = self.create_base_product(
            name='Other Product',
            slug='other-product',
            price='300.00',
        )
        StockPorTalla.objects.create(producto=other_product, talla='L', cantidad=3)

        response = self.client.get(
            reverse('products:product_list'),
            {
                'q': 'Test',
                'category': self.category.slug,
                'size': 'M',
                'min_price': '50',
                'max_price': '150',
            },
        )

        self.assertEqual(response.status_code, 200)
        products = list(response.context['products'])
        self.assertIn(self.product, products)
        self.assertNotIn(other_product, products)

    def test_filtro_por_talla_solo_muestra_productos_con_stock(self):
        _, _, no_stock_product = self.create_base_product(
            name='No Stock Product',
            slug='no-stock-product',
        )
        StockPorTalla.objects.create(producto=no_stock_product, talla='M', cantidad=0)
        _, _, other_size_product = self.create_base_product(
            name='Other Size Product',
            slug='other-size-product',
        )
        StockPorTalla.objects.create(producto=other_size_product, talla='L', cantidad=4)

        products = list(ProductoRepository().buscar(talla='M'))

        self.assertIn(self.product, products)
        self.assertNotIn(no_stock_product, products)
        self.assertNotIn(other_size_product, products)

    def test_product_detail_shows_ordered_stock(self):
        StockPorTalla.objects.create(producto=self.product, talla='XS', cantidad=1)

        response = self.client.get(reverse('products:product_detail', args=[self.product.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item.talla for item in response.context['inventory_items']], ['XS', 'M'])


@override_settings(ALLOWED_HOSTS=['testserver'])
class ProductApiTest(ProductTestMixin, TestCase):
    def setUp(self):
        self.category, self.brand, self.product = self.create_base_product()
        StockPorTalla.objects.create(producto=self.product, talla='M', cantidad=5)
        _, _, self.inactive_product = self.create_base_product(
            name='Inactive Product',
            slug='inactive-product',
            active=False,
        )

    def test_product_api_list_is_public_and_returns_active_products(self):
        response = self.client.get(reverse('products_api:product_list'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload['results']), 1)
        self.assertEqual(payload['results'][0]['slug'], self.product.slug)
        self.assertEqual(
            payload['results'][0]['detail_url'],
            f'http://testserver{reverse("products_api:product_detail", args=[self.product.slug])}',
        )

    def test_public_product_service_uses_public_route(self):
        response = self.client.get(reverse('products_api:product_list'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['results'][0]['name'], self.product.nombre)
        self.assertIn('/api/public/products/', payload['results'][0]['detail_url'])

    def test_product_api_filters_results(self):
        _, _, expensive_product = self.create_base_product(
            name='Expensive Product',
            slug='expensive-product',
            price='500.00',
        )
        StockPorTalla.objects.create(producto=expensive_product, talla='L', cantidad=2)

        response = self.client.get(
            reverse('products_api:product_list'),
            {
                'q': 'Test',
                'category': self.category.slug,
                'size': 'M',
                'min_price': '50',
                'max_price': '150',
            },
        )

        self.assertEqual(response.status_code, 200)
        slugs = [item['slug'] for item in response.json()['results']]
        self.assertEqual(slugs, [self.product.slug])

    def test_product_api_detail_returns_product_data(self):
        response = self.client.get(reverse('products_api:product_detail', args=[self.product.slug]))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['slug'], self.product.slug)
        self.assertEqual(payload['brand']['slug'], self.brand.slug)
        self.assertEqual(payload['stock_total'], 5)
        self.assertEqual(payload['stock_by_size'], [{'size': 'M', 'quantity': 5}])

    def test_product_api_detail_returns_json_404_for_inactive_or_missing_product(self):
        inactive_response = self.client.get(
            reverse('products_api:product_detail', args=[self.inactive_product.slug])
        )
        missing_response = self.client.get(reverse('products_api:product_detail', args=['missing']))

        self.assertEqual(inactive_response.status_code, 404)
        self.assertEqual(missing_response.status_code, 404)
        self.assertEqual(inactive_response['content-type'], 'application/json')
