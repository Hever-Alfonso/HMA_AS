# README de Arquitectura - UNLABELED

UNLABELED es una tienda de ropa en línea desarrollada con Django, PostgreSQL y Docker para el curso de Arquitectura de Software. El sistema permite a clientes explorar un catálogo de productos, filtrar prendas por criterios comerciales, gestionar un carrito de compras, registrarse, iniciar sesión y finalizar órdenes con validación de inventario por talla.

## Objetivo del Sistema

El objetivo funcional es ofrecer una experiencia de e-commerce para la marca UNLABELED, centralizando:

- Catálogo público de productos activos.
- Consulta de productos por categoría, búsqueda, talla, rango de precios y ordenamiento.
- Detalle de producto con imágenes, descripción, precio, marca, categoría y stock por talla.
- Carrito para visitantes usando sesión.
- Carrito persistente para usuarios autenticados.
- Merge de carrito de sesión hacia base de datos al iniciar sesión.
- Checkout autenticado con datos de envío.
- Creación de órdenes con descuento de stock.
- Cancelación de órdenes con restauración de inventario.
- API pública JSON para integración con otros equipos.
- Internacionalización básica en español e inglés.
- Administración mediante Django Admin.

## Tecnologías

| Tecnología | Uso |
| --- | --- |
| Python 3.11 | Runtime de la aplicación dentro del contenedor Docker. |
| Django 5.1.6 | Framework web principal. |
| PostgreSQL 15 | Base de datos relacional para desarrollo con Docker. |
| Docker / Docker Compose | Orquestación local de `web` y `db`. |
| Pillow | Manejo de imágenes de productos y categorías. |
| python-dotenv | Carga de variables desde `.env`. |
| Gunicorn | Servidor WSGI definido en el Dockerfile para escenarios productivos. |
| React 18 por CDN | Selector interactivo de cantidad en la vista del carrito. |
| Django i18n | Soporte de idiomas español e inglés con `LocaleMiddleware`. |

## Vista General de Arquitectura

El proyecto usa el patrón MVT de Django, equivalente en responsabilidades al enfoque MVC:

- **Model / Modelo:** modelos Django en `models.py`.
- **View / Controlador:** CBVs en `views.py`, encargadas de recibir requests, validar entrada básica y delegar.
- **Template / Vista:** HTML en `templates/`, con textos internacionalizados mediante `{% trans %}` y `{% blocktranslate %}`.

Sobre esta base se agregó una capa explícita de servicios y adaptadores para separar lógica de negocio, cumplir inversión de dependencias y evitar que las vistas concentren reglas de dominio.

## Estructura de Aplicaciones

| App | Responsabilidad |
| --- | --- |
| `core` | Home, about, base template, mixins reutilizables, managers y modelos abstractos. |
| `accounts` | Usuario personalizado, autenticación, registro, login, logout, perfil y roles. |
| `products` | Catálogo, productos, marcas, categorías, imágenes, stock por talla, repositorio, servicios de inventario y API pública. |
| `cart` | Carrito de sesión, carrito persistente, contrato abstracto de backend, adaptadores y merge al login. |
| `orders` | Checkout, órdenes, ítems de orden, cancelación, cálculo de envío y reglas transaccionales. |

## Capas y Responsabilidades

### Presentación

La presentación vive en templates Django bajo cada app:

- `core/templates/core/`
- `accounts/templates/usuarios/`
- `products/templates/products/`
- `cart/templates/cart/`
- `orders/templates/orders/`

Los templates extienden `core/base.html` y usan bloques de traducción para cumplir el requisito de dos idiomas. La interfaz mantiene una identidad visual consistente con navegación principal, footer, formularios estilizados, filtros laterales y mensajes de usuario.

### Controladores / CBVs

Las vistas son Class-Based Views. Su responsabilidad principal es:

- Leer parámetros del request.
- Resolver objetos con `get_object_or_404` o querysets.
- Delegar lógica de negocio a servicios.
- Preparar contexto para templates.
- Retornar JSON en la API pública.

Ejemplos:

- `products.views.ProductListView` delega filtros a `ProductoRepository`.
- `cart.views.CartAddView`, `CartUpdateView` y `CartRemoveView` delegan en `CartService`.
- `orders.views.CheckoutView` delega creación de orden en `OrdenService`.

### Servicios

La lógica de negocio compleja está separada en servicios:

| Servicio | Archivo | Responsabilidad |
| --- | --- | --- |
| `InventoryService` | `products/services.py` | Validar tallas, validar disponibilidad, descontar y restaurar stock con bloqueo transaccional. |
| `CartService` | `cart/services.py` | Agregar, actualizar y eliminar ítems, decidiendo si usar sesión o base de datos. |
| `CartMergeService` | `cart/services.py` | Fusionar carrito de sesión con carrito persistente al iniciar sesión. La base de datos tiene precedencia ante conflictos. |
| `OrdenService` | `orders/services.py` | Crear órdenes desde carrito, calcular envío, descontar inventario, marcar como pagada y limpiar carritos. |

El uso de servicios responde directamente al feedback de la primera entrega, que pedía extraer reglas de sincronización, carrito y checkout fuera de las vistas.

### Repositorio

`products/repositories.py` contiene `ProductoRepository`, que centraliza consultas de productos:

- Búsqueda por texto.
- Filtro por categoría, marca, rango de precios y talla disponible.
- Ordenamiento por novedad o precio.
- Optimización con `select_related` para `marca` y `categoria`.
- Optimización con `prefetch_related` para `stock_por_talla` e `imagenes`.

Esta capa reduce duplicación y evita queries N+1 en catálogo, detalle y API.

### Dominio / Modelos

Los modelos representan las entidades principales:

- `accounts.Usuario`: usuario personalizado con `telefono` y `rol`.
- `products.Categoria`: categoría de producto con slug e imagen.
- `products.Marca`: marca con slug.
- `products.Producto`: prenda con precio, descripción, imagen, marca, categoría, estado activo y soft delete.
- `products.StockPorTalla`: inventario por combinación producto/talla.
- `products.ImagenProducto`: galería de imágenes adicionales.
- `cart.Carrito`: carrito persistente asociado a usuario o sesión.
- `cart.ItemCarrito`: ítems del carrito con producto, talla, cantidad y precio unitario.
- `orders.Orden`: orden de compra con estado, datos de envío, costo de envío y total.
- `orders.ItemOrden`: copia transaccional de productos comprados.

También existen modelos abstractos reutilizables:

- `TimestampMixin`: agrega `created_at` y `updated_at`.
- `SoftDeleteMixin`: permite borrado lógico.
- `ActivableMixin`: permite activar/desactivar registros.

## Inversión de Dependencias

El proyecto implementa inversión de dependencias en dos zonas.

### Carrito

`cart/base.py` define la abstracción `CartBackend`.

Implementaciones concretas:

- `SessionCartBackend` en `cart/session_backend.py`.
- `DatabaseCartBackend` en `cart/db_backend.py`.

`CartService` depende del contrato común y decide qué backend usar según el estado de autenticación del usuario. Esto cumple la recomendación del feedback de la primera entrega: separar sesión y base de datos bajo una interfaz común.

### Costo de Envío

`orders/shipping.py` define `ShippingRateProvider`.

Implementaciones concretas:

- `ExternalExchangeRateShippingRateProvider`: consume una API externa de tasa USD/COP.
- `FixedShippingRateProvider`: devuelve una tarifa fija de respaldo.

`ShippingRateProviderFactory` selecciona la estrategia mediante `SHIPPING_RATE_PROVIDER`. Esta solución cubre el requisito de consumir un servicio externo y mantiene un fallback para ambientes sin Internet.

## Lógica de Negocio Principal

### Catálogo y Búsqueda

El flujo del catálogo es:

1. `ProductListView` recibe parámetros `q`, `category`, `size`, `min_price`, `max_price` y `sort`.
2. `ProductoRepository.buscar()` construye el queryset.
3. Se aplican filtros combinados.
4. Se retornan productos activos paginados.

Los productos inactivos o borrados lógicamente no aparecen en las consultas públicas.

### Inventario por Talla

El inventario se modela con `StockPorTalla`, no como un stock global del producto. Esto permite validar compras por variante:

- Producto A, talla M, 5 unidades.
- Producto A, talla L, 0 unidades.

`InventoryService` centraliza:

- Validación de talla.
- Validación de cantidad positiva.
- Validación de disponibilidad.
- Descuento de stock con `select_for_update()`.
- Restauración de stock al cancelar una orden.

### Carrito

El carrito tiene una llave compuesta `producto_id:talla`, lo que evita mezclar tallas distintas del mismo producto.

Visitantes:

- Usan `cart.Cart`, almacenado en sesión.

Usuarios autenticados:

- Usan `Carrito` e `ItemCarrito` en base de datos.
- Después de cada cambio, la sesión se sincroniza desde la base de datos.

Login:

- La señal `user_logged_in` ejecuta `CartMergeService.merge_session_into_db`.
- Si existe conflicto entre sesión y base de datos, prevalece el carrito persistente.
- Los ítems no conflictivos de la sesión se agregan a la base de datos.

### Checkout

El flujo de compra es:

1. El usuario autenticado entra a `/orders/checkout/`.
2. `CheckoutForm` valida dirección, ciudad, código postal y teléfono.
3. `OrdenService.crear_desde_carrito()` valida que el carrito no esté vacío.
4. Se calcula el costo de envío usando el proveedor configurado.
5. Se crea la orden.
6. Por cada ítem se descuenta stock con `InventoryService.decrease_stock()`.
7. Se crean los `ItemOrden`.
8. Se calcula el total.
9. La orden se marca como pagada.
10. Se limpian carrito de sesión y carrito persistente.

Todo el proceso se ejecuta dentro de `transaction.atomic`, de modo que una falla de stock o validación revierte la operación.

### Cancelación de Órdenes

La cancelación:

1. Valida que la orden no esté enviada ni entregada.
2. Restaura el stock de cada ítem.
3. Cambia el estado a `cancelada`.

También se ejecuta de forma atómica para mantener consistencia entre orden e inventario.

## API Pública JSON

La aplicación expone endpoints públicos bajo `/api/public/` para que otros equipos puedan consumir información del catálogo.

| Método | Ruta | Descripción |
| --- | --- | --- |
| `GET` | `/api/public/products/` | Lista productos activos. |
| `GET` | `/api/public/products/<slug>/` | Detalle de un producto activo. |

Filtros soportados:

- `q`
- `category`
- `size`
- `min_price`
- `max_price`
- `sort`

El serializer `ProductApiSerializer` genera estructuras JSON estables con nombre, slug, descripción, precio, marca, categoría, imagen, URL de detalle y stock por talla.

## Internacionalización

El proyecto tiene i18n configurado en `HMA_AS/settings.py`:

- `LANGUAGE_CODE = 'es'`
- `LANGUAGES = [('es', 'Español'), ('en', 'English')]`
- `LocaleMiddleware`
- `LOCALE_PATHS = [BASE_DIR / 'locale']`
- Archivos `.po` y `.mo` en `locale/es/` y `locale/en/`

Los templates usan `{% trans %}` y `{% blocktranslate %}`. Las validaciones y mensajes de servicios/modelos usan `gettext_lazy` o `gettext`.

## Calidad, Validaciones y Performance

Mejoras incorporadas frente al feedback de la primera entrega:

- Imports del login desacoplados de lógica de carrito.
- Merge de carritos extraído a `CartMergeService`.
- Constante de orden de tallas movida a `products/constants.py`.
- Validadores en forms y modelos.
- Permisos de acceso a órdenes: un usuario no puede consultar órdenes de otro.
- `select_related` y `prefetch_related` para catálogo, detalle y API.
- Índices en campos consultados frecuentemente como `slug`, `activo`, `precio`, `producto/talla` y `usuario/estado`.
- Tests automatizados para modelos, filtros, API, carrito, merge, checkout, permisos y proveedor externo.

## Pruebas Automatizadas

Las pruebas se distribuyen por app:

- `products/tests.py`: modelos, slugs, stock, filtros de catálogo, detalle y API pública.
- `cart/tests.py`: llave compuesta producto/talla, incremento de cantidad, total, merge y sincronización autenticada.
- `orders/tests.py`: checkout vacío, stock insuficiente, orden pagada, proveedor externo y permisos.
- `accounts/tests.py`: validación del teléfono en formularios.

Durante pruebas, `settings.py` cambia la base de datos a SQLite (`test.sqlite3`) si detecta `test` en `sys.argv`, para no depender de PostgreSQL.

Comando:

```powershell
docker compose exec web python manage.py test
```

## Docker y Persistencia

`docker-compose.yml` define dos servicios:

- `db`: PostgreSQL 15, expuesto en el puerto `5432`, con datos persistidos en `postgres_data/data`.
- `web`: Django, expuesto en el puerto `8000`, con migraciones automáticas antes de iniciar `runserver`.

El Dockerfile usa `python:3.11-slim`, instala dependencias del sistema, instala `requirements.txt` y deja Gunicorn como comando base.

## Alcance Frente al Entregable 2

| Requisito | Estado en el repo |
| --- | --- |
| Correcciones de entrega 1 | Implementadas en carrito, servicios, constantes, validaciones y tests. |
| Arquitectura MVC/MVT + servicios | Implementada con CBVs, templates, modelos, servicios y repositorio. |
| Dos idiomas | Implementado con Django i18n, español e inglés. |
| Dos pruebas unitarias simples | Superado: hay múltiples pruebas en varias apps. |
| Servicio web JSON propio | Implementado en `/api/public/products/`. |
| Consumo de API externa | Implementado para cálculo de envío con tasa USD/COP. |
| Inversión de dependencias | Implementada en carrito y proveedor de envío. |
| Docker | Implementado con Dockerfile y Docker Compose. |
| Despliegue GCP | No se encontró configuración específica de GCP en el repo; el proyecto sí está preparado para ejecutarse en contenedor. |
| Consumo del servicio del equipo precedente | No se encontró una integración visible en el código actual. |

## Variables de Entorno Relevantes

| Variable | Uso |
| --- | --- |
| `SECRET_KEY` | Llave secreta de Django. |
| `DEBUG` | Activa modo desarrollo. |
| `ALLOWED_HOSTS` | Hosts permitidos. |
| `DB_NAME` | Nombre de base de datos. |
| `DB_USER` | Usuario de PostgreSQL. |
| `DB_PASSWORD` | Contraseña de PostgreSQL. |
| `DB_HOST` | Host de PostgreSQL. |
| `DB_PORT` | Puerto de PostgreSQL. |
| `SHIPPING_RATE_PROVIDER` | Proveedor de envío: `external` o `fixed`. |
| `EXCHANGE_RATE_API_URL` | API de tasa USD/COP. |
| `BASE_SHIPPING_USD` | Base de envío en dólares. |
| `FIXED_SHIPPING_RATE` | Tarifa fija de respaldo en COP. |
| `SHIPPING_API_TIMEOUT` | Timeout de la API externa. |

## Rutas Principales

| Ruta | Descripción |
| --- | --- |
| `/` | Home con productos destacados. |
| `/about/` | Página informativa de la marca. |
| `/shop/` | Catálogo. |
| `/shop/category/<slug>/` | Catálogo por categoría. |
| `/shop/<slug>/` | Detalle de producto. |
| `/cart/` | Carrito. |
| `/orders/checkout/` | Checkout autenticado. |
| `/orders/<orden_id>/` | Detalle de orden. |
| `/orders/<orden_id>/cancelar/` | Cancelación de orden. |
| `/accounts/registro/` | Registro. |
| `/accounts/login/` | Login. |
| `/accounts/logout/` | Logout. |
| `/accounts/perfil/` | Perfil. |
| `/api/public/products/` | API pública de productos. |
| `/admin/` | Django Admin. |

## Principios Aplicados

- **SRP:** servicios separados para carrito, inventario, órdenes y envío.
- **DIP:** abstracciones para backends de carrito y proveedores de envío.
- **Repository:** consultas complejas de productos centralizadas.
- **Strategy / Factory:** proveedor de envío externo o fijo.
- **Transaction Script controlado:** checkout y cancelación dentro de transacciones atómicas.
- **Soft Delete:** productos pueden marcarse como eliminados sin borrado físico.
- **DRY:** mixins y managers reutilizables en `core`.
- **Optimización de consultas:** `select_related`, `prefetch_related` e índices.

