"""
Management command para poblar la base de datos con productos de ropa de prueba.
No requiere datasets externos — genera imágenes placeholder con PIL.
"""

import random
from decimal import Decimal
from io import BytesIO

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile

from PIL import Image, ImageDraw, ImageFont

from products.models import Categoria, Marca, Producto, StockPorTalla


# ---------------------------------------------------------------------------
# Paleta de colores por categoría (R, G, B)
# ---------------------------------------------------------------------------
COLORES_CATEGORIA = {
    'Camiseta':  (74,  144, 226),
    'Pantalón':  (80,  80,  80),
    'Suéter':    (184, 92,  56),
    'Vestido':   (210, 80,  140),
    'Abrigo':    (60,  100, 60),
    'Sandalia':  (226, 180, 60),
    'Camisa':    (100, 160, 200),
    'Zapatilla': (200, 60,  60),
    'Bolso':     (140, 100, 180),
    'Bota':      (100, 70,  40),
}

DESCRIPCIONES_CATEGORIAS = {
    'Camiseta':  'Camisetas casuales y deportivas para toda ocasión.',
    'Pantalón':  'Pantalones de vestir, casuales y deportivos.',
    'Suéter':    'Suéteres cálidos y cómodos para clima frío.',
    'Vestido':   'Vestidos elegantes para eventos y uso diario.',
    'Abrigo':    'Abrigos y chaquetas para protegerte del frío.',
    'Sandalia':  'Sandalias cómodas para el verano.',
    'Camisa':    'Camisas formales e informales de alta calidad.',
    'Zapatilla': 'Zapatillas deportivas y de uso diario.',
    'Bolso':     'Bolsos y accesorios de moda.',
    'Bota':      'Botas resistentes y con estilo.',
}

CATEGORIAS = list(COLORES_CATEGORIA.keys())

MARCAS = ['Opulence', 'Vanguard', 'Élan', 'NovaTrend', 'Aether', 'Luxen', 'Prism', 'Velour']

# Adjetivos y materiales para generar nombres de productos variados
ADJETIVOS = [
    'Clásic@', 'Moderno/a', 'Elegante', 'Deportiv@', 'Urban@', 'Casual',
    'Premium', 'Slim', 'Oversized', 'Vintage', 'Minimalista', 'Exclusiv@',
    'Esencial', 'Atemporal', 'Liger@', 'Cómodo/a', 'Estructurado/a', 'Fluido/a',
]

MATERIALES = [
    'Algodón', 'Lino', 'Poliéster', 'Denim', 'Lana', 'Cuero', 'Nylon',
    'Seda', 'Franela', 'Jersey', 'Tweed', 'Viscosa',
]

COLORES_PRENDA = [
    'Negro', 'Blanco', 'Azul marino', 'Gris', 'Beige', 'Rojo', 'Verde oliva',
    'Mostaza', 'Coral', 'Lavanda', 'Tostado', 'Azul cielo', 'Terracota',
]

# ---------------------------------------------------------------------------
# Generación de imágenes placeholder
# ---------------------------------------------------------------------------

def generar_imagen_placeholder(categoria: str, nombre: str, size: tuple = (400, 400)) -> bytes:
    """
    Genera una imagen PNG sencilla con el color de la categoría,
    un degradado, y el nombre del producto como texto.
    """
    color_base = COLORES_CATEGORIA.get(categoria, (120, 120, 120))

    img = Image.new('RGB', size, color_base)
    draw = ImageDraw.Draw(img)

    # Degradado sutil: líneas horizontales ligeramente más claras arriba
    for y in range(size[1]):
        factor = 1.0 - (y / size[1]) * 0.3
        r = min(255, int(color_base[0] * factor))
        g = min(255, int(color_base[1] * factor))
        b = min(255, int(color_base[2] * factor))
        draw.line([(0, y), (size[0], y)], fill=(r, g, b))

    # Rectángulo de fondo para el texto
    text_bg_y = size[1] - 70
    draw.rectangle([(0, text_bg_y), (size[0], size[1])], fill=(0, 0, 0, 180))

    # Texto: categoría arriba, nombre abajo (truncado si es largo)
    try:
        font_grande = ImageFont.load_default(size=22)
        font_chico  = ImageFont.load_default(size=15)
    except Exception:
        font_grande = ImageFont.load_default()
        font_chico  = ImageFont.load_default()

    draw.text((10, text_bg_y + 8),  categoria,                  fill='white', font=font_grande)
    draw.text((10, text_bg_y + 38), nombre[:40],                fill=(220, 220, 220), font=font_chico)

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def generar_imagen_categoria(categoria: str, size: tuple = (400, 300)) -> bytes:
    """Genera imagen de portada para una categoría."""
    color_base = COLORES_CATEGORIA.get(categoria, (120, 120, 120))

    img = Image.new('RGB', size, color_base)
    draw = ImageDraw.Draw(img)

    # Degradado
    for y in range(size[1]):
        factor = 0.7 + (y / size[1]) * 0.3
        r = min(255, int(color_base[0] * factor))
        g = min(255, int(color_base[1] * factor))
        b = min(255, int(color_base[2] * factor))
        draw.line([(0, y), (size[0], y)], fill=(r, g, b))

    # Nombre de categoría centrado
    try:
        font = ImageFont.load_default(size=32)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), categoria, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size[0] - text_w) // 2
    y = (size[1] - text_h) // 2

    # Sombra
    draw.text((x + 2, y + 2), categoria, fill=(0, 0, 0, 100), font=font)
    draw.text((x, y),         categoria, fill='white',         font=font)

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# Generación de nombres y descripciones de productos
# ---------------------------------------------------------------------------

def generar_nombre_producto(categoria: str, marca: str, color: str, material: str) -> str:
    adjetivo = random.choice(ADJETIVOS).replace('@', random.choice(['a', 'o']))
    adjetivo = adjetivo.replace('/a', random.choice(['', 'a', 'o']))
    return f'{categoria} {adjetivo} {color} — {material} | {marca}'


def generar_descripcion(nombre: str, categoria: str, marca: str, color: str, material: str) -> str:
    templates = [
        (
            f'Descubre la {categoria.lower()} perfecta de {marca}. Confeccionada en {material.lower()} '
            f'de primera calidad en tono {color.lower()}, esta prenda combina comodidad y estilo '
            f'para cualquier ocasión. Su diseño contemporáneo la hace versátil y duradera.'
        ),
        (
            f'{nombre} es una de las piezas más solicitadas de la colección {marca}. '
            f'Elaborada con {material.lower()} seleccionado, ofrece una textura suave y un acabado '
            f'impecable en color {color.lower()}. Ideal para el día a día o eventos especiales.'
        ),
        (
            f'La {categoria.lower()} {color.lower()} de {marca} redefine el concepto de moda accesible. '
            f'Fabricada en {material.lower()} de alta resistencia, es una inversión en estilo que '
            f'perdura temporada tras temporada. Disponible en todas las tallas.'
        ),
    ]
    return random.choice(templates)


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = 'Pobla la base de datos con categorías, marcas y productos de ropa de prueba'

    def add_arguments(self, parser):
        parser.add_argument(
            '--productos',
            type=int,
            default=50,
            help='Número de productos a crear (default: 50)',
        )
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Elimina todos los productos existentes antes de poblar',
        )

    def handle(self, *args, **options):
        num_productos = options['productos']

        if options['limpiar']:
            self.stdout.write(self.style.WARNING('Eliminando productos existentes...'))
            StockPorTalla.objects.all().delete()
            Producto.all_objects.all().delete()
            Categoria.objects.all().delete()
            Marca.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Base de datos limpiada.'))

        # ── Categorías ──────────────────────────────────────────────────────
        self.stdout.write('Creando categorías...')
        categorias = {}
        for nombre in CATEGORIAS:
            categoria, created = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': DESCRIPCIONES_CATEGORIAS[nombre]},
            )
            if created or not categoria.imagen_portada:
                png_data = generar_imagen_categoria(nombre)
                categoria.imagen_portada.save(
                    f'categoria_{nombre.lower().replace(" ", "_")}.png',
                    ContentFile(png_data),
                    save=True,
                )
            categorias[nombre] = categoria
            status = 'creada' if created else 'ya existía'
            self.stdout.write(f'  {nombre}: {status}')

        # ── Marcas ───────────────────────────────────────────────────────────
        self.stdout.write('Creando marcas...')
        marcas = []
        for nombre_marca in MARCAS:
            marca, created = Marca.objects.get_or_create(nombre=nombre_marca)
            marcas.append(marca)
            status = 'creada' if created else 'ya existía'
            self.stdout.write(f'  {nombre_marca}: {status}')

        # ── Productos ────────────────────────────────────────────────────────
        self.stdout.write(f'\nCreando {num_productos} productos...')
        tallas = [t[0] for t in StockPorTalla.Talla.choices]
        creados = 0
        existentes = 0

        for i in range(num_productos):
            categoria_nombre = random.choice(CATEGORIAS)
            categoria = categorias[categoria_nombre]
            marca     = random.choice(marcas)
            color     = random.choice(COLORES_PRENDA)
            material  = random.choice(MATERIALES)

            nombre = generar_nombre_producto(categoria_nombre, marca.nombre, color, material)
            # Asegurar unicidad añadiendo índice si hace falta
            nombre_final = nombre if len(nombre) <= 200 else nombre[:197] + '...'

            # Precio entre $29.900 y $499.900 (múltiplo de 100 COP)
            precio = Decimal(str(random.randint(299, 4999))) * Decimal('100')

            producto, created = Producto.objects.get_or_create(
                nombre=nombre_final,
                defaults={
                    'descripcion': generar_descripcion(
                        nombre_final, categoria_nombre, marca.nombre, color, material
                    ),
                    'precio':   precio,
                    'marca':    marca,
                    'categoria': categoria,
                },
            )

            if created:
                # Imagen placeholder
                png_data = generar_imagen_placeholder(categoria_nombre, nombre_final)
                slug_img = f'producto_{i + 1:04d}_{categoria_nombre.lower().replace(" ", "_")}.png'
                producto.imagen.save(slug_img, ContentFile(png_data), save=True)

                # Stock por talla
                for talla in tallas:
                    StockPorTalla.objects.get_or_create(
                        producto=producto,
                        talla=talla,
                        defaults={'cantidad': random.randint(0, 30)},
                    )
                creados += 1
                if creados % 10 == 0:
                    self.stdout.write(f'  ... {creados} productos creados')
            else:
                existentes += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'¡Listo! {creados} productos creados en {len(CATEGORIAS)} categorías y {len(MARCAS)} marcas.'
        ))
        if existentes:
            self.stdout.write(f'({existentes} ya existían y no fueron modificados)')
        self.stdout.write(
            f'\nEjecuta: docker compose exec web python manage.py populate_db --productos {num_productos}'
        )
