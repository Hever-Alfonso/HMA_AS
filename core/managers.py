from django.db import models


class SoftDeleteManager(models.Manager):
    """Manager que excluye registros borrados por defecto"""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def deleted(self):
        return super().get_queryset().filter(is_deleted=True)

    def with_deleted(self):
        return super().get_queryset()


class ActiveManager(models.Manager):
    """Manager que retorna solo registros activos"""

    def get_queryset(self):
        return super().get_queryset().filter(activo=True)
