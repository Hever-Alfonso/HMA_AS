# HMA_AS — Comandos de referencia

Este documento describe todos los comandos necesarios para ejecutar, poblar y administrar el proyecto.

## Conceptos clave

- **Imagen**: plantilla construida a partir del Dockerfile.
- **Contenedor**: instancia en ejecución de una imagen.
- **Contenedores son efímeros**: si se recrean, su sistema de archivos interno se pierde.
- **Volumen (bind mount)**: en este proyecto, `postgres_data/data/` guarda la base de datos PostgreSQL directamente en la carpeta del proyecto, haciéndola portable y persistente al zipar.

---

## Correr el proyecto con Docker (recomendado)

### Paso 1: Levantar los contenedores

Desde la carpeta raíz del proyecto (donde está `docker-compose.yml`):
```bash
docker compose up --build
```

Esperar hasta ver este mensaje:
```
unlabeled_web | Starting development server at http://0.0.0.0:8000/
```

### Paso 2: Poblar la base de datos con productos de prueba

Abrir una segunda terminal y ejecutar:
```bash
docker compose exec web python manage.py populate_db
```

Resultado esperado:
```
¡Listo! Se crearon 50 productos en 10 categorías.
```

### Paso 3: Crear superusuario administrador

```bash
docker compose exec web python manage.py createsuperuser
```

### Paso 4: Abrir en el navegador

Tienda (usuario final):
```
http://localhost:8000
```

Panel de administración:
```
http://localhost:8000/admin/
```

Desde otra máquina en la misma red (reemplaza con tu IP local):
```
http://192.168.X.X:8000
```

---

## Comandos Django dentro del contenedor

Aplicar migraciones:
```bash
docker compose exec web python manage.py migrate
```

Crear migraciones nuevas:
```bash
docker compose exec web python manage.py makemigrations
```

Abrir la consola interactiva de Django:
```bash
docker compose exec web python manage.py shell
```

Correr cualquier comando de Django:
```bash
docker compose exec web python manage.py <comando>
```

---

## Comandos útiles de Docker

Levantar en segundo plano (sin ocupar la terminal):
```bash
docker compose up -d
```

Ver los logs en tiempo real:
```bash
docker compose logs -f
```

Detener los contenedores:
```bash
docker compose down
```

Reconstruir la imagen sin caché:
```bash
docker compose build --no-cache
```

---

## Reinicio total (borrar todos los datos)

Detener contenedores y eliminar datos persistentes:
```bash
docker compose down
rm -rf postgres_data/data/*
rm -rf media/productos/*
rm -rf media/categorias/*
```

Volver a levantar desde cero:
```bash
docker compose up --build
```

En segunda terminal:
```bash
docker compose exec web python manage.py populate_db
docker compose exec web python manage.py createsuperuser
```

---

## Nota sobre persistencia

La carpeta `postgres_data/data/` contiene la base de datos de PostgreSQL.
Al zipar el proyecto con esa carpeta incluida, todos los datos (usuarios, productos, órdenes) se conservan.
Solo se pierden si se elimina manualmente con el comando de reinicio total indicado arriba.
