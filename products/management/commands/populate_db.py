import csv
import os
import random
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from products.models import Categoria, Marca, Producto, StockPorTalla

LABEL_MAP = {
    0: ("Camiseta",      "Prendas superiores tipo camiseta o top."),
    1: ("Pantalon",      "Pantalones y jeans de todo tipo."),
    2: ("Pullover",      "Suéteres y pullovers de punto."),
    3: ("Vestido",       "Vestidos para toda ocasión."),
    4: ("Abrigo",        "Abrigos y chaquetas de temporada."),
    5: ("Sandalia",      "Sandalias y calzado abierto."),
    6: ("Camisa",        "Camisas formales e informales."),
    7: ("Zapatilla",     "Zapatillas deportivas y casuales."),
    8: ("Bolso",         "Bolsos, carteras y accesorios."),
    9: ("Bota",          "Botas y calzado de caña alta."),
}

BRANDS = ["Nike", "Adidas", "Zara", "H&M", "Levi's", "Gucci", "Puma", "Uniqlo"]

PRODUCTS_PER_CATEGORY = 5

TALLAS = ["XS", "S", "M", "L", "XL"]


def pixels_to_png(pixel_values):
    """Convierte 784 valores de píxeles en un PNG de 28x28 en escala de grises."""
    from PIL import Image
    img = Image.new("L", (28, 28))
    img.putdata([int(p) for p in pixel_values])
    img = img.resize((128, 128), Image.NEAREST)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class Command(BaseCommand):
    help = "Pobla la base de datos con productos del dataset Fashion MNIST"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            default="archive/fashion-mnist_train.csv",
            help="Ruta al CSV de Fashion MNIST (relativa a la raíz del proyecto)",
        )

    def handle(self, *args, **options):
        csv_path = options["csv"]

        if not os.path.exists(csv_path):
            self.stderr.write(f"No se encontró el archivo: {csv_path}")
            return

        self.stdout.write("Creando marcas...")
        marcas = []
        for nombre in BRANDS:
            marca, _ = Marca.objects.get_or_create(nombre=nombre)
            marcas.append(marca)

        self.stdout.write("Creando categorías...")
        categorias = {}
        for label_id, (nombre, descripcion) in LABEL_MAP.items():
            cat, _ = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={"descripcion": descripcion},
            )
            categorias[label_id] = cat

        self.stdout.write("Leyendo CSV y creando productos...")

        # Agrupar filas por etiqueta
        rows_by_label = {i: [] for i in range(10)}
        with open(csv_path, newline="") as f:
            reader = csv.reader(f)
            next(reader)  # saltar encabezado
            for row in reader:
                label = int(row[0])
                if len(rows_by_label[label]) < PRODUCTS_PER_CATEGORY:
                    rows_by_label[label].append(row[1:])
                if all(len(v) >= PRODUCTS_PER_CATEGORY for v in rows_by_label.values()):
                    break

        created_count = 0
        for label_id, rows in rows_by_label.items():
            categoria = categorias[label_id]
            cat_nombre = LABEL_MAP[label_id][0]

            for i, pixels in enumerate(rows, start=1):
                nombre = f"{cat_nombre} Modelo {i}"
                precio = round(random.uniform(19.99, 199.99), 2)
                marca = random.choice(marcas)

                producto, created = Producto.all_objects.get_or_create(
                    nombre=nombre,
                    defaults={
                        "descripcion": f"{cat_nombre} de alta calidad, modelo {i}. Comodidad y estilo garantizados.",
                        "precio": precio,
                        "marca": marca,
                        "categoria": categoria,
                    },
                )

                if created:
                    # Generar imagen desde píxeles
                    png_bytes = pixels_to_png(pixels)
                    filename = f"{categoria.slug}_modelo_{i}.png"
                    producto.imagen.save(filename, ContentFile(png_bytes), save=True)

                    # Crear stock por talla
                    for talla in TALLAS:
                        StockPorTalla.objects.get_or_create(
                            producto=producto,
                            talla=talla,
                            defaults={"cantidad": random.randint(5, 50)},
                        )
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"¡Listo! Se crearon {created_count} productos en {len(categorias)} categorías."
        ))
