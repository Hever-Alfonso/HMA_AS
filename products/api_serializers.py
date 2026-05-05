from django.urls import reverse

from .constants import SIZE_ORDER


class ProductApiSerializer:
    """Convierte productos en estructuras JSON estables para integraciones externas."""

    def __init__(self, request):
        self.request = request

    def serialize_list_item(self, product):
        """Devuelve la informacion resumida de un producto."""
        image_url = self._build_media_url(product.imagen)

        return {
            'id': product.id,
            'name': product.nombre,
            'slug': product.slug,
            'description': product.descripcion,
            'price': str(product.precio),
            'brand': product.marca.nombre,
            'category': product.categoria.nombre,
            'image': image_url,
            'image_url': image_url,
            'detail_url': self._build_product_detail_url(product.slug),
        }

    def serialize_detail(self, product):
        """Devuelve la informacion completa de un producto."""
        image_url = self._build_media_url(product.imagen)
        stock_items = sorted(
            product.stock_por_talla.all(),
            key=lambda item: (
                SIZE_ORDER.index(item.talla)
                if item.talla in SIZE_ORDER
                else len(SIZE_ORDER)
            ),
        )

        return {
            'id': product.id,
            'name': product.nombre,
            'slug': product.slug,
            'description': product.descripcion,
            'price': str(product.precio),
            'brand': {
                'name': product.marca.nombre,
                'slug': product.marca.slug,
            },
            'category': {
                'name': product.categoria.nombre,
                'slug': product.categoria.slug,
            },
            'image': image_url,
            'image_url': image_url,
            'stock_total': product.stock_total,
            'stock_by_size': [
                {'size': item.talla, 'quantity': item.cantidad}
                for item in stock_items
            ],
            'images': [
                {
                    'url': self._build_media_url(image.imagen),
                    'order': image.orden,
                    'is_main': image.es_principal,
                }
                for image in product.imagenes.all()
            ],
        }

    def _build_media_url(self, image_field):
        if not image_field:
            return None
        return self.request.build_absolute_uri(image_field.url)

    def _build_product_detail_url(self, slug):
        return self.request.build_absolute_uri(
            reverse('products_api:product_detail', kwargs={'slug': slug})
        )
