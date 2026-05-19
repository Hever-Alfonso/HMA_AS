# UNLABELED - Ecommerce de ropa

Proyecto desarrollado para el Entregable 2 de Arquitectura de Software 2026-1 en la Universidad EAFIT.

UNLABELED es una tienda de ropa en línea construida con Django, PostgreSQL y Docker. La aplicación permite explorar productos, filtrar el catálogo, gestionar carrito de compras, registrarse, iniciar sesión y completar órdenes con control de inventario por talla.

---

## Integrantes

| Nombre | Rol |
| --- | --- |
| Hever Andre Alfonso Jimenez | Arquitecto |
| Andrés Felipe Garnica Roa | Desarrollador |
| Moises Arturo Vergara Garces | Desarrollador |

---

## Funcionalidades implementadas

- Catálogo público de productos activos.
- Detalle de producto con galería, tallas disponibles, cantidad y productos relacionados.
- Filtros por búsqueda, categoría, talla, precio mínimo, precio máximo y ordenamiento.
- Paginación del catálogo.
- Usuario personalizado con teléfono y rol (`cliente` / `admin`).
- Registro, login, logout y perfil de usuario.
- Carrito de compras por sesión para visitantes.
- Carrito persistente en base de datos para usuarios autenticados.
- Sincronización del carrito de sesión con el carrito persistente al iniciar sesión.
- Validación de stock por talla antes de agregar o actualizar productos en el carrito.
- Checkout autenticado con formulario de dirección, ciudad, código postal y teléfono.
- Creación de órdenes desde el carrito con transacción atómica.
- Descuento de inventario al pagar una orden.
- Restauración de inventario al cancelar una orden.
- Cálculo de costo de envío con proveedor externo de tasa USD/COP y proveedor fijo de respaldo.
- API pública JSON para consulta de productos.
- Panel de administración Django para usuarios, productos, categorías, marcas, stock y órdenes.
- Internacionalización básica en español e inglés mediante `LocaleMiddleware` y archivos `locale/`.
- Datos iniciales mediante fixture y comando de carga `populate_db`.
- Pruebas automatizadas para productos, API pública, carrito, checkout, permisos de órdenes y formularios.

---

## Tecnologías

- Python 3.11
- Django 5.1.6
- PostgreSQL 15
- Docker y Docker Compose
- Pillow
- python-dotenv
- Gunicorn
- React 18 vía CDN para el selector de cantidades del carrito

---

## Arquitectura

El proyecto sigue el patrón MVT de Django y separa responsabilidades por aplicaciones.

| App | Responsabilidad |
| --- | --- |
| `accounts` | Usuario personalizado, autenticación, registro, perfil y roles. |
| `core` | Páginas base, mixins, managers reutilizables y vistas generales. |
| `products` | Catálogo, categorías, marcas, productos, imágenes, stock por talla, repositorio, servicios de inventario y API pública. |
| `cart` | Carrito en sesión, carrito persistente en BD, backends, sincronización y operaciones de agregar, actualizar y eliminar. |
| `orders` | Checkout, órdenes, ítems de orden, cancelación, cálculo de envío y reglas transaccionales. |

### Patrones y principios aplicados

- **MVT**: separación entre modelos, vistas y templates.
- **Repository**: `ProductoRepository` centraliza consultas y filtros de productos.
- **Service Layer**: `InventoryService`, `CartService`, `CartMergeService` y `OrdenService` concentran reglas de negocio.
- **Strategy / Factory**: proveedores de envío intercambiables en `orders/shipping.py`.
- **Adapter**: backends de carrito para sesión y base de datos bajo un contrato común.
- **DRY**: mixins y managers reutilizables en `core`.
- **Soft Delete**: productos con borrado lógico mediante `SoftDeleteMixin`.
- **Transacciones atómicas**: creación y cancelación de órdenes con control de stock.

---

## Estructura del proyecto

```text
HMA_AS/
├── HMA_AS/                    # Configuración principal del proyecto Django
├── accounts/                  # Usuarios, autenticación y formularios
├── cart/                      # Carrito de compras, backends y sincronización
├── core/                      # Home, about, mixins y managers reutilizables
├── locale/                    # Traducciones es/en
├── media/                     # Archivos subidos o generados
├── orders/                    # Checkout, órdenes, envío y cancelaciones
├── products/                  # Catálogo, API pública, inventario y fixtures
│   ├── fixtures/
│   │   └── initial_data.json
│   └── management/
│       └── commands/
│           └── populate_db.py
├── static/                    # CSS e imágenes estáticas
├── postgres_data/             # Datos persistentes de PostgreSQL
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── requirements.txt
├── COMMANDS.md
└── README.md
```

---

## Rutas principales

| Ruta | Descripción | Acceso |
| --- | --- | --- |
| `/` | Página de inicio con productos destacados | Público |
| `/about/` | Página informativa de la marca | Público |
| `/shop/` | Catálogo de productos | Público |
| `/shop/category/<slug>/` | Catálogo filtrado por categoría | Público |
| `/shop/<slug>/` | Detalle de producto | Público |
| `/cart/` | Detalle del carrito | Público |
| `/cart/add/` | Agregar producto al carrito | POST |
| `/cart/update/` | Actualizar cantidad del carrito | POST |
| `/cart/remove/` | Eliminar producto del carrito | POST |
| `/orders/checkout/` | Checkout | Autenticado |
| `/orders/<orden_id>/` | Detalle de orden | Dueño de la orden |
| `/orders/<orden_id>/cancelar/` | Cancelar orden y restaurar stock | Dueño de la orden |
| `/accounts/registro/` | Registro de usuario | Público |
| `/accounts/login/` | Inicio de sesión | Público |
| `/accounts/logout/` | Cierre de sesión | Público |
| `/accounts/perfil/` | Perfil del usuario | Autenticado |
| `/i18n/` | Cambio de idioma de Django | Público |
| `/admin/` | Panel de administración Django | Administrador |

---

## API pública JSON

La aplicación expone endpoints públicos para que otros equipos puedan consumir información del catálogo.

| Método | Ruta | Descripción |
| --- | --- | --- |
| `GET` | `/api/public/products/` | Lista productos activos. |
| `GET` | `/api/public/products/<slug>/` | Retorna el detalle de un producto activo. |

### Filtros del listado

| Parámetro | Ejemplo | Descripción |
| --- | --- | --- |
| `q` | `/api/public/products/?q=shirt` | Busca por nombre o descripción. |
| `category` | `/api/public/products/?category=t-shirts` | Filtra por slug de categoría. |
| `size` | `/api/public/products/?size=M` | Filtra productos con stock disponible en una talla. |
| `min_price` | `/api/public/products/?min_price=50000` | Precio mínimo. |
| `max_price` | `/api/public/products/?max_price=150000` | Precio máximo. |
| `sort` | `/api/public/products/?sort=price_asc` | Ordena por `newest`, `price_asc` o `price_desc`. |

### Ejemplo de respuesta del listado

```json
{
  "results": [
    {
      "id": 1,
      "name": "Classic T-Shirt",
      "slug": "classic-t-shirt",
      "description": "Basic cotton t-shirt.",
      "price": "85000.00",
      "brand": "UNLABELED",
      "category": "T-Shirts",
      "image": "http://localhost:8000/media/productos/classic.jpg",
      "image_url": "http://localhost:8000/media/productos/classic.jpg",
      "detail_url": "http://localhost:8000/api/public/products/classic-t-shirt/"
    }
  ]
}
```

### Ejemplo de respuesta del detalle

```json
{
  "id": 1,
  "name": "Classic T-Shirt",
  "slug": "classic-t-shirt",
  "description": "Basic cotton t-shirt.",
  "price": "85000.00",
  "brand": {
    "name": "UNLABELED",
    "slug": "unlabeled"
  },
  "category": {
    "name": "T-Shirts",
    "slug": "t-shirts"
  },
  "image": "http://localhost:8000/media/productos/classic.jpg",
  "image_url": "http://localhost:8000/media/productos/classic.jpg",
  "stock_total": 12,
  "stock_by_size": [
    {
      "size": "M",
      "quantity": 5
    }
  ],
  "images": []
}
```

---

## Configuración

El proyecto carga variables desde `.env` con `python-dotenv`.

| Variable | Valor por defecto | Descripción |
| --- | --- | --- |
| `SECRET_KEY` | `django-insecure-default-key` | Llave secreta de Django. |
| `DEBUG` | `False` | Activa o desactiva modo debug. |
| `ALLOWED_HOSTS` | `127.0.0.1,localhost` | Hosts permitidos separados por coma. |
| `DB_NAME` | `unlabeled_db` | Nombre de la base de datos. |
| `DB_USER` | `postgres` | Usuario de PostgreSQL. |
| `DB_PASSWORD` | `postgres` | Contraseña de PostgreSQL. |
| `DB_HOST` | `localhost` | Host de PostgreSQL. |
| `DB_PORT` | `5432` | Puerto de PostgreSQL. |
| `SHIPPING_RATE_PROVIDER` | `external` | Proveedor de envío: `external` o `fixed`. |
| `EXCHANGE_RATE_API_URL` | `https://open.er-api.com/v6/latest/USD` | API usada para tasa USD/COP. |
| `BASE_SHIPPING_USD` | `4.00` | Tarifa base de envío en USD. |
| `FIXED_SHIPPING_RATE` | `15000.00` | Tarifa fija de respaldo en COP. |
| `SHIPPING_API_TIMEOUT` | `3` | Timeout del proveedor externo en segundos. |

---

## Ejecución con Docker

### Requisitos

- Docker Desktop instalado y en ejecución.

### Levantar el proyecto

```bash
docker compose up --build
```

El contenedor web ejecuta migraciones automáticamente y levanta el servidor en:

```text
http://localhost:8000
```

### Poblar datos iniciales

En otra terminal:

```bash
docker compose exec web python manage.py populate_db
```

### Crear administrador

```bash
docker compose exec web python manage.py createsuperuser
```

Panel de administración:

```text
http://localhost:8000/admin/
```

---

## Comandos útiles

Aplicar migraciones:

```bash
docker compose exec web python manage.py migrate
```

Crear migraciones:

```bash
docker compose exec web python manage.py makemigrations
```

Ejecutar pruebas:

```bash
docker compose exec web python manage.py test
```

Abrir shell de Django:

```bash
docker compose exec web python manage.py shell
```

Ver logs:

```bash
docker compose logs -f
```

Detener contenedores:

```bash
docker compose down
```

---

## Ejecución local sin Docker

Si se usa ejecución local, se requiere PostgreSQL disponible y variables de entorno configuradas.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py populate_db
python manage.py runserver
```

---

## Persistencia y reinicio

PostgreSQL persiste datos en:

```text
postgres_data/data/
```

Los archivos de medios se almacenan en:

```text
media/
```

Para reiniciar completamente el entorno:

```bash
docker compose down
rm -rf postgres_data/data/*
rm -rf media/productos/*
rm -rf media/categorias/*
docker compose up --build
```

En Windows PowerShell, el borrado equivalente puede hacerse con:

```powershell
Remove-Item -Recurse -Force postgres_data\data\*
Remove-Item -Recurse -Force media\productos\*
Remove-Item -Recurse -Force media\categorias\*
```

---

## Pruebas automatizadas

El proyecto incluye pruebas para:

- Validaciones de productos, precios, slugs y stock.
- Filtros del catálogo.
- API pública de productos.
- Carrito por sesión.
- Carrito persistente para usuarios autenticados.
- Merge de carrito al iniciar sesión.
- Checkout con carrito vacío, stock insuficiente y orden pagada.
- Proveedor externo de envío.
- Permisos de acceso a órdenes.
- Validación de teléfono en formularios de usuario.

Comando:

```bash
docker compose exec web python manage.py test
```

Durante pruebas, la configuración cambia automáticamente a SQLite (`test.sqlite3`) para evitar depender de PostgreSQL.

---

## Documentación complementaria

- `COMMANDS.md`: comandos frecuentes para Docker y Django.

---

## Autores

- Hever Andre Alfonso Jimenez - Universidad EAFIT - Arquitectura de Software 2026-1
- Andrés Felipe Garnica Roa - Universidad EAFIT - Arquitectura de Software 2026-1
- Moises Arturo Vergara Garces - Universidad EAFIT - Arquitectura de Software 2026-1
