# Entregable 1 - Arquitectura de Software 2026-1
# HMA_AS — Tienda de Ropa en Línea

Proyecto desarrollado como parte del Entregable 1 de Arquitectura de Software en la Universidad EAFIT.
Consiste en un e-commerce de ropa construido con Django, PostgreSQL y Docker, aplicando la arquitectura MVT y principios de diseño como DRY y ETC.

---

## Integrantes

| Nombre | Rol |
|--------|-----|
| Hever Andre Alfonso Jimenez | Arquitecto |
| Andrés Felipe Garnica Roa | Desarrollador |
| Moises Arturo Vergara Garces | Desarrollador |

---

## Descripción del proyecto

La aplicación es una tienda de ropa en línea orientada al mercado colombiano. Permite a los usuarios explorar productos organizados por categorías y marcas, gestionar un carrito de compras y realizar órdenes. Los administradores tienen acceso a un panel separado desde donde pueden gestionar el inventario y los pedidos.

**Alcance:**
- Catálogo de productos con categorías, marcas y stock por talla
- Carrito de compras por sesión
- Sistema de órdenes con seguimiento de estados
- Sistema de autenticación con roles (cliente / administrador)
- Panel de administración independiente de la vista del usuario final
- Datos de productos generados a partir del dataset **Fashion MNIST**

**Actores:**
- **Cliente**: navega el catálogo, agrega productos al carrito, realiza órdenes
- **Administrador**: gestiona productos, categorías, marcas, stock y órdenes

---

## Tecnologías utilizadas

- Python 3.11
- Django 5.1.6
- PostgreSQL 15
- Docker y Docker Compose
- Pillow (manejo de imágenes)
- Fashion MNIST (datos de prueba)
- Git y GitHub

---

## Arquitectura MVT

El proyecto sigue el patrón **Modelo - Vista - Template** de Django:

### Modelos (apps)
- `accounts` — Usuario personalizado con roles (cliente / administrador)
- `core` — Mixins reutilizables: TimestampMixin, SoftDeleteMixin, ActivableMixin
- `products` — Producto, Categoria, Marca, StockPorTalla, ImagenProducto
- `cart` — Carrito de compras basado en sesiones
- `orders` — Orden e ItemOrden con estados y datos de envío

### Vistas
- Vistas basadas en clases (CBV): ListView, DetailView, CreateView, TemplateView
- LoginRequiredMixin para proteger rutas de usuarios no autenticados
- Separación estricta entre vistas de usuario final y vistas de administrador

### Templates
- Todos extienden `base.html`
- Organizados por app dentro de sus respectivas carpetas `templates/`

---

## Estructura del proyecto

```
HMA_AS/
├── HMA_AS/                   # Configuración principal del proyecto
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/                 # App de usuarios y autenticación
├── core/                     # Mixins y managers reutilizables
├── products/                 # Catálogo de productos
│   └── management/
│       └── commands/
│           └── populate_db.py  # Comando para poblar la BD con Fashion MNIST
├── cart/                     # Carrito de compras
├── orders/                   # Órdenes y seguimiento
├── static/                   # Archivos estáticos (CSS, JS, imágenes)
├── media/                    # Imágenes subidas/generadas (no en git)
├── archive/                  # Dataset Fashion MNIST (CSV + binarios)
├── postgres_data/            # Datos persistentes de PostgreSQL (no en git)
│   └── data/
├── templates/                # Templates base del proyecto
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
├── COMMANDS.md
└── README.md
```

---

## Rutas principales

| Ruta | Descripción | Acceso |
|------|-------------|--------|
| `/` | Página de inicio | Público |
| `/shop/` | Catálogo de productos | Público |
| `/shop/<slug>/` | Detalle de producto | Público |
| `/cart/` | Carrito de compras | Autenticado |
| `/orders/` | Historial de órdenes | Autenticado |
| `/accounts/login/` | Inicio de sesión | Público |
| `/accounts/register/` | Registro de usuario | Público |
| `/admin/` | Panel de administración Django | Administrador |

---

## Cómo ejecutar el proyecto

### Requisitos previos
- Docker Desktop instalado y corriendo

### Paso 1: Levantar los contenedores

```bash
docker compose up --build
```

Esperar hasta ver:
```
unlabeled_web | Starting development server at http://0.0.0.0:8000/
```

### Paso 2: Poblar la base de datos (en una segunda terminal)

```bash
docker compose exec web python manage.py populate_db
```

Esto crea 10 categorías, 8 marcas y 50 productos con imágenes generadas desde el dataset Fashion MNIST.

### Paso 3: Crear superusuario (administrador)

```bash
docker compose exec web python manage.py createsuperuser
```

### Paso 4: Abrir en el navegador

```
http://localhost:8000
```

Panel de administración:
```
http://localhost:8000/admin/
```

---

## Persistencia de datos

Los datos de PostgreSQL se almacenan en la carpeta local `postgres_data/data/`, lo que permite preservar usuarios, productos y órdenes al zipar y compartir el proyecto.

Para reiniciar todo desde cero:
```bash
docker compose down
rm -rf postgres_data/data/*
rm -rf media/productos/*
rm -rf media/categorias/*
```

---

## Principios aplicados

- **DRY**: Mixins en `core/` reutilizados en todos los modelos (TimestampMixin, SoftDeleteMixin, ActivableMixin) y managers compartidos (SoftDeleteManager, ActiveManager)
- **ETC**: Modelos desacoplados entre apps, configuración sensible manejada via variables de entorno
- **MVT**: Separación clara entre modelos, vistas y templates
- **SoftDelete**: Los productos eliminados no se borran físicamente de la base de datos

---

## Autores

- Hever Andre Alfonso Jimenez — Universidad EAFIT — Arquitectura de Software 2026-1
- Andrés Felipe Garnica Roa — Universidad EAFIT — Arquitectura de Software 2026-1
- Moises Arturo Vergara Garces — Universidad EAFIT — Arquitectura de Software 2026-1
