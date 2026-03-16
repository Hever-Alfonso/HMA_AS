"""
Management command para poblar la base de datos con productos de prueba
usando el dataset Fashion MNIST almacenado en archive/.
"""

import os
import struct
import random
from decimal import Decimal
from io import BytesIO

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings

from PIL import Image

from products.models import Categoria, Marca, Producto, StockPorTalla


# Etiquetas reales del dataset Fashion MNIST
FASHION_MNIST_LABELS = {
    0: 'Camiseta',
    1: 'Pantalón',
    2: 'Suéter',
    3: 'Vestido',
    4: 'Abrigo',
    5: 'Sandalia',
    6: 'Camisa',
    7: 'Zapatilla',
    8: 'Bolso',
    9: 'Bota',
}

DESCRIPCIONES_CATEGORIAS = {
    'Camiseta': 'Camisetas casuales y deportivas para toda ocasión.',
    'Pantalón': 'Pantalones de vestir, casuales y deportivos.',
    'Suéter': 'Suéteres cálidos y cómodos para clima frío.',
    'Vestido': 'Vestidos elegantes para eventos y uso diario.',
    'Abrigo': 'Abrigos y chaquetas para protegerte del frío.',
    'Sandalia': 'Sandalias cómodas para el verano.',
    'Camisa': 'Camisas formales e informales de alta calidad.',
    'Zapatilla': 'Zapatillas deportivas y de uso diario.',
    'Bolso': 'Bolsos y accesorios de moda.',
    'Bota': 'Botas resistentes y con estilo.',
}

MARCAS = [
    'Opulence',
    'Vanguard',
    'Élan',
    'NovaTrend',
    'Aether',
    'Luxen',
    'Prism',
    'Velour',
]


def leer_imagenes_idx(ruta_imagenes):
    """Lee archivo binario IDX3 de Fashion MNIST y devuelve array de imágenes."""
    with open(ruta_imagenes, 'rb') as f:
        magic, num_images, rows, cols = struct.unpack('>IIII', f.read(16))
        if magic != 2051:
            raise ValueError(f'Archivo IDX inválido (magic={magic}, esperado=2051)')
        data = f.read()
        # Convertir a lista de imágenes (cada una es bytes de rows*cols)
        images = []
        img_size = rows * cols
        for i in range(num_images):
            offset = i * img_size
            pixel_data = data[offset:offset + img_size]
            images.append((pixel_data, rows, cols))
    return images


def leer_labels_idx(ruta_labels):
    """Lee archivo binario IDX1 de labels de Fashion MNIST."""
    with open(ruta_labels, 'rb') as f:
        magic, num_labels = struct.unpack('>II', f.read(8))
        if magic != 2049:
            raise ValueError(f'Archivo IDX inválido (magic={magic}, esperado=2049)')
        labels = list(f.read())
    return labels


def generar_imagen_png(pixel_data, rows, cols, size=(280, 280)):
    """Convierte datos de píxeles en una imagen PNG escalada."""
    img = Image.frombytes('L', (cols, rows), pixel_data)
    img = img.resize(size, Image.NEAREST)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


class Command(BaseCommand):
    help = 'Pobla la base de datos con categorías, marcas y productos de prueba usando Fashion MNIST'

    def add_arguments(self, parser):
        parser.add_argument(
            '--productos',
            type=int,
            default=50,
            help='Número de productos a crear (default: 50)',
        )

    def handle(self, *args, **options):
        num_productos = options['productos']
        archive_dir = os.path.join(settings.BASE_DIR, 'archive')

        ruta_imagenes = os.path.join(archive_dir, 'train-images-idx3-ubyte')
        ruta_labels = os.path.join(archive_dir, 'train-labels-idx1-ubyte')

        # Verificar que los archivos existan
        if not os.path.exists(ruta_imagenes):
            self.stderr.write(self.style.ERROR(
                f'No se encontró el archivo de imágenes: {ruta_imagenes}'
            ))
            return

        if not os.path.exists(ruta_labels):
            self.stderr.write(self.style.ERROR(
                f'No se encontró el archivo de labels: {ruta_labels}'
            ))
            return

        self.stdout.write('Leyendo dataset Fashion MNIST...')
        images = leer_imagenes_idx(ruta_imagenes)
        labels = leer_labels_idx(ruta_labels)

        # --- Crear categorías ---
        self.stdout.write('Creando categorías...')
        categorias = {}
        # Agrupar imágenes por label para elegir imagen representativa
        imagenes_por_label = {}
        for i, label in enumerate(labels):
            if label not in imagenes_por_label:
                imagenes_por_label[label] = []
            if len(imagenes_por_label[label]) < 100:  # Solo guardar las primeras 100
                imagenes_por_label[label].append(i)

        for label_id, nombre in FASHION_MNIST_LABELS.items():
            categoria, created = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'descripcion': DESCRIPCIONES_CATEGORIAS.get(nombre, ''),
                }
            )
            # Asignar imagen de portada si no tiene una
            if not categoria.imagen_portada and label_id in imagenes_por_label:
                idx = imagenes_por_label[label_id][0]
                pixel_data, rows, cols = images[idx]
                png_data = generar_imagen_png(pixel_data, rows, cols)
                categoria.imagen_portada.save(
                    f'categoria_{nombre.lower()}.png',
                    ContentFile(png_data),
                    save=True,
                )
            categorias[label_id] = categoria
            status = 'creada' if created else 'ya existía'
            self.stdout.write(f'  - {nombre}: {status}')

        # --- Crear marcas ---
        self.stdout.write('Creando marcas...')
        marcas = []
        for nombre_marca in MARCAS:
            marca, created = Marca.objects.get_or_create(nombre=nombre_marca)
            marcas.append(marca)
            status = 'creada' if created else 'ya existía'
            self.stdout.write(f'  - {nombre_marca}: {status}')

        # --- Crear productos ---
        self.stdout.write(f'Creando {num_productos} productos...')
        tallas = [t[0] for t in StockPorTalla.Talla.choices]
        productos_creados = 0
        productos_existentes = 0

        # Seleccionar imágenes aleatorias para los productos
        indices_aleatorios = random.sample(range(len(images)), min(num_productos, len(images)))

        for i, img_idx in enumerate(indices_aleatorios):
            label = labels[img_idx]
            categoria = categorias[label]
            marca = random.choice(marcas)

            nombre_producto = f'{categoria.nombre} {marca.nombre} #{i + 1:03d}'
            precio = Decimal(str(random.randint(2990, 49990))) * Decimal('10')  # $29.900 - $499.900

            producto, created = Producto.objects.get_or_create(
                nombre=nombre_producto,
                defaults={
                    'descripcion': f'{nombre_producto} — Prenda de alta calidad de la marca {marca.nombre}. '
                                   f'Categoría: {categoria.nombre}. Ideal para cualquier ocasión.',
                    'precio': precio,
                    'marca': marca,
                    'categoria': categoria,
                }
            )

            if created:
                # Generar y guardar imagen
                pixel_data, rows, cols = images[img_idx]
                png_data = generar_imagen_png(pixel_data, rows, cols)
                producto.imagen.save(
                    f'producto_{i + 1:03d}.png',
                    ContentFile(png_data),
                    save=True,
                )

                # Crear stock por talla
                for talla in tallas:
                    StockPorTalla.objects.get_or_create(
                        producto=producto,
                        talla=talla,
                        defaults={'cantidad': random.randint(0, 30)},
                    )
                productos_creados += 1
            else:
                productos_existentes += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'¡Listo! Se crearon {productos_creados} productos en {len(FASHION_MNIST_LABELS)} categorías.'
        ))
        if productos_existentes:
            self.stdout.write(
                f'({productos_existentes} productos ya existían y no se modificaron)'
            )
