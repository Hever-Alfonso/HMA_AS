# Onboarding del Proyecto - UNLABELED

Este documento sirve como guía de entrada para cualquier integrante que necesite entender, correr, probar y modificar el proyecto UNLABELED.

## Contexto del Proyecto

UNLABELED es un e-commerce de ropa multimarca desarrollado en Django. La aplicación permite explorar productos, filtrar catálogo, manejar carrito, registrarse, iniciar sesión, hacer checkout y administrar productos, usuarios, stock y órdenes desde Django Admin.

El proyecto fue ajustado para la segunda entrega con foco en:

- Arquitectura MVT/MVC con separación por capas.
- Servicios para lógica de negocio.
- Inversión de dependencias.
- API pública JSON.
- Consumo de API externa.
- Docker.
- Internacionalización español/inglés.
- Pruebas automatizadas.

## Requisitos Previos

Recomendado:

- Docker Desktop instalado y ejecutándose.
- Git instalado.
- PowerShell en Windows.

No se recomienda correrlo directamente con Python local si no tienes Python 3.11. El proyecto está preparado para ejecutarse con Docker usando `python:3.11-slim`.

## Estructura Principal

```text
HMA_AS/
├── HMA_AS/                  # Configuración principal de Django
├── accounts/                # Usuarios, autenticación, formularios y roles
├── cart/                    # Carrito de sesión, carrito BD, servicios y backends
├── core/                    # Home, base template, mixins, managers y modelos abstractos
├── locale/                  # Traducciones español/inglés
├── media/                   # Imágenes cargadas o generadas
├── orders/                  # Checkout, órdenes, envío y cancelaciones
├── products/                # Catálogo, stock, API, repositorio y fixtures
├── static/                  # CSS e imágenes estáticas
├── postgres_data/           # Datos persistentes de PostgreSQL con Docker
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── requirements.txt
├── README.md
├── README_ARQUITECTURA.md
└── ONBOARDING.md
```

## Cómo Correr el Proyecto con Docker

Ubícate en la raíz real del repo:

```powershell
cd C:\Users\TU_USER\HMA_AS
```

Construye y levanta los contenedores:

```powershell
docker compose up --build
```

Espera un mensaje parecido a:

```text
Starting development server at http://0.0.0.0:8000/
```

Abre la aplicación:

```text
http://localhost:8000
```

Abre el admin:

```text
http://localhost:8000/admin/
```

## Poblar Datos de Prueba

En otra terminal, desde la misma carpeta:

```powershell
docker compose exec web python manage.py populate_db
```

Este comando crea categorías, marcas, productos, stock por talla e imágenes placeholder.

## Crear Superusuario

```powershell
docker compose exec web python manage.py createsuperuser
```

Luego entra al admin:

```text
http://localhost:8000/admin/
```

## Comandos Frecuentes

Aplicar migraciones:

```powershell
docker compose exec web python manage.py migrate
```

Crear migraciones:

```powershell
docker compose exec web python manage.py makemigrations
```

Correr pruebas:

```powershell
docker compose exec web python manage.py test
```

Abrir shell de Django:

```powershell
docker compose exec web python manage.py shell
```

Ver logs:

```powershell
docker compose logs -f
```

Detener contenedores:

```powershell
docker compose down
```

Levantar en segundo plano:

```powershell
docker compose up -d
```

## Flujo Funcional para Probar Manualmente

1. Entra a `http://localhost:8000`.
2. Abre `/shop/`.
3. Filtra por categoría, talla o precio.
4. Entra al detalle de un producto.
5. Selecciona talla y cantidad.
6. Agrega al carrito.
7. Regístrate o inicia sesión.
8. Revisa que el carrito se mantenga después del login.
9. Ve a checkout.
10. Completa dirección, ciudad, código postal y teléfono.
11. Finaliza la compra.
12. Revisa la orden creada.
13. Cancela la orden si quieres validar restauración de stock.

## Apps y Dónde Tocar Código

### `accounts`

Toca esta app si vas a modificar:

- Registro.
- Login/logout.
- Perfil.
- Modelo de usuario.
- Validaciones del formulario de usuario.
- Roles `cliente` y `admin`.

Archivos frecuentes:

- `accounts/models.py`
- `accounts/forms.py`
- `accounts/views.py`
- `accounts/templates/usuarios/`
- `accounts/tests.py`

### `products`

Toca esta app si vas a modificar:

- Productos.
- Categorías.
- Marcas.
- Stock por talla.
- Filtros del catálogo.
- API pública.
- Datos iniciales.

Archivos frecuentes:

- `products/models.py`
- `products/repositories.py`
- `products/services.py`
- `products/views.py`
- `products/api_serializers.py`
- `products/api_urls.py`
- `products/management/commands/populate_db.py`
- `products/tests.py`

### `cart`

Toca esta app si vas a modificar:

- Carrito de sesión.
- Carrito persistente.
- Sincronización entre sesión y BD.
- Merge al iniciar sesión.
- Contrato abstracto de backends de carrito.

Archivos frecuentes:

- `cart/cart.py`
- `cart/base.py`
- `cart/session_backend.py`
- `cart/db_backend.py`
- `cart/services.py`
- `cart/signals.py`
- `cart/models.py`
- `cart/views.py`
- `cart/tests.py`

### `orders`

Toca esta app si vas a modificar:

- Checkout.
- Creación de órdenes.
- Cancelación.
- Restauración de stock.
- Cálculo de envío.
- Consumo de API externa de tasa USD/COP.

Archivos frecuentes:

- `orders/models.py`
- `orders/forms.py`
- `orders/services.py`
- `orders/shipping.py`
- `orders/views.py`
- `orders/tests.py`

### `core`

Toca esta app si vas a modificar:

- Home.
- About.
- Base visual.
- Mixins reutilizables.
- Managers de soft delete y activos.

Archivos frecuentes:

- `core/models.py`
- `core/managers.py`
- `core/mixins.py`
- `core/views.py`
- `core/templates/core/`

## Lógica de Negocio Clave

### Catálogo

`ProductListView` no arma consultas complejas directamente. Delega en `ProductoRepository.buscar()`.

La consulta soporta:

- Texto (`q`).
- Categoría (`category`).
- Talla (`size`).
- Precio mínimo (`min_price`).
- Precio máximo (`max_price`).
- Orden (`sort`).

### Stock

El stock se controla por talla en `StockPorTalla`.

Para modificar inventario usa `InventoryService`, no actualices cantidades directamente desde vistas:

- `InventoryService.validate_available()`
- `InventoryService.decrease_stock()`
- `InventoryService.increase_stock()`

### Carrito

La llave del carrito es `producto_id:talla`.

Esto permite que el mismo producto en talla M y talla L sean dos ítems distintos.

Para modificar el carrito usa `CartService`:

- `CartService.add_item()`
- `CartService.update_item()`
- `CartService.remove_item()`

### Merge de Carrito

Cuando un usuario inicia sesión, `cart/signals.py` escucha `user_logged_in` y ejecuta:

```python
CartMergeService.merge_session_into_db(request, user)
```

Política de conflicto:

- Si el producto/talla ya existe en BD, se conserva la cantidad de BD.
- Si el producto/talla solo existe en sesión, se agrega a BD.
- Al final, la sesión se reconstruye desde BD.

### Checkout

Para crear órdenes usa `OrdenService.crear_desde_carrito()`.

Este servicio:

- Valida carrito no vacío.
- Calcula envío.
- Crea la orden.
- Descuenta stock.
- Crea ítems.
- Calcula total.
- Marca como pagada.
- Limpia carritos.

El proceso está envuelto en `transaction.atomic`.

## API Pública

Endpoints:

```text
GET /api/public/products/
GET /api/public/products/<slug>/
```

Ejemplos:

```text
http://localhost:8000/api/public/products/
http://localhost:8000/api/public/products/?size=M&sort=price_asc
```

La API se implementa con:

- `products/api_urls.py`
- `products/views.py`
- `products/api_serializers.py`
- `products/repositories.py`

## API Externa de Envío

El costo de envío se calcula con `orders/shipping.py`.

Por defecto usa:

```text
https://open.er-api.com/v6/latest/USD
```

Variables importantes:

- `SHIPPING_RATE_PROVIDER=external`
- `EXCHANGE_RATE_API_URL=https://open.er-api.com/v6/latest/USD`
- `BASE_SHIPPING_USD=4.00`
- `FIXED_SHIPPING_RATE=15000.00`
- `SHIPPING_API_TIMEOUT=3`

Para pruebas o desarrollo sin Internet se puede usar:

```text
SHIPPING_RATE_PROVIDER=fixed
```

## Internacionalización

Los idiomas disponibles son español e inglés.

Al agregar texto visible:

- En templates usa `{% trans "Texto" %}`.
- Para bloques largos usa `{% blocktranslate %}`.
- En Python usa `gettext_lazy` o `gettext`.
- Evita textos quemados en vistas o templates.

Archivos:

- `locale/es/LC_MESSAGES/django.po`
- `locale/en/LC_MESSAGES/django.po`

Si modificas traducciones, compila mensajes:

```powershell
docker compose exec web django-admin compilemessages
```

## Convenciones de Código

Reglas principales:

- Seguir PEP 8.
- Imports al inicio del archivo.
- Vistas como CBVs.
- Rutas por app con `app_name`.
- Lógica de negocio en `services.py`.
- Consultas de productos en `ProductoRepository`.
- Cambios de stock con `InventoryService`.
- Operaciones de compra/cancelación con transacciones.
- Agregar tests cuando cambies reglas de negocio.

## Pruebas Recomendadas Antes de Subir Cambios

Ejecuta:

```powershell
docker compose exec web python manage.py test
```

También es útil revisar que Django arranque:

```powershell
docker compose exec web python manage.py check
```

Para probar la API:

```powershell
Invoke-RestMethod http://localhost:8000/api/public/products/
```

## Troubleshooting

### El puerto 8000 está ocupado

Cambia el puerto del servicio `web` en `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"
```

Luego abre:

```text
http://localhost:8001
```

### El puerto 5432 está ocupado

Otro PostgreSQL local puede estar usando el puerto. Cambia el puerto externo:

```yaml
ports:
  - "5433:5432"
```

### Quiero reiniciar todo desde cero

Detén contenedores:

```powershell
docker compose down
```

Borra datos persistentes de PostgreSQL:

```powershell
Remove-Item -Recurse -Force postgres_data\data\*
```

Opcionalmente borra imágenes generadas:

```powershell
Remove-Item -Recurse -Force media\productos\*
Remove-Item -Recurse -Force media\categorias\*
```

Vuelve a levantar:

```powershell
docker compose up --build
```

Y repuebla:

```powershell
docker compose exec web python manage.py populate_db
```

## Flujo Recomendado para Desarrollar

1. Actualiza tu rama local.
2. Levanta Docker.
3. Reproduce el flujo que vas a cambiar.
4. Modifica código en la app correspondiente.
5. Agrega o ajusta tests.
6. Ejecuta pruebas.
7. Revisa `git diff`.
8. Haz commit con un mensaje claro.
9. Sube la rama.

Comandos base:

```powershell
git status
git diff
docker compose exec web python manage.py test
git add .
git commit -m "docs: agrega arquitectura y onboarding"
git push
```