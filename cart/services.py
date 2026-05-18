from django.db import transaction

from products.services import InventoryService

from .db_backend import DatabaseCartBackend
from .session_backend import SessionCartBackend


class CartService:
    """Centraliza reglas de negocio del carrito."""

    @staticmethod
    def validate_item(producto, talla, cantidad):
        InventoryService.validate_available(producto, talla, cantidad)

    @staticmethod
    def should_persist(request):
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated)

    @staticmethod
    def sync_session_from_db(request, db_backend):
        session_backend = SessionCartBackend(request.session)
        session_backend.clear()
        for db_item in db_backend.get_items():
            session_backend.set_item(
                db_item['producto'],
                db_item['talla'],
                db_item['cantidad'],
            )

    @classmethod
    def add_item(cls, request, producto, talla, cantidad):
        cls.validate_item(producto, talla, cantidad)
        if cls.should_persist(request):
            db_backend = DatabaseCartBackend(request.user)
            db_backend.add_item(producto, talla, cantidad)
            cls.sync_session_from_db(request, db_backend)
            return

        SessionCartBackend(request.session).add_item(producto, talla, cantidad)

    @classmethod
    def update_item(cls, request, producto, talla, cantidad):
        if cantidad <= 0:
            cls.remove_item(request, producto, talla)
            return

        cls.validate_item(producto, talla, cantidad)
        if cls.should_persist(request):
            db_backend = DatabaseCartBackend(request.user)
            db_backend.set_item(producto, talla, cantidad)
            cls.sync_session_from_db(request, db_backend)
            return

        SessionCartBackend(request.session).update_item(producto, talla, cantidad)

    @staticmethod
    def remove_item(request, producto, talla):
        if CartService.should_persist(request):
            db_backend = DatabaseCartBackend(request.user)
            db_backend.remove_item(producto, talla)
            CartService.sync_session_from_db(request, db_backend)
            return

        SessionCartBackend(request.session).remove_item(producto, talla)


class CartMergeService:
    """Sincroniza carrito de sesion y BD con precedencia para la BD."""

    @staticmethod
    @transaction.atomic
    def merge_session_into_db(request, user):
        session_backend = SessionCartBackend(request.session)
        db_backend = DatabaseCartBackend(user)

        existing_keys = {
            item['key']
            for item in db_backend.get_items()
        }

        for session_item in session_backend.get_items():
            if session_item['key'] in existing_keys:
                continue

            db_backend.add_item(
                session_item['producto'],
                session_item['talla'],
                session_item['cantidad'],
            )

        session_backend.clear()
        for db_item in db_backend.get_items():
            session_backend.set_item(
                db_item['producto'],
                db_item['talla'],
                db_item['cantidad'],
            )
