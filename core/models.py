from django.db import models
from django.utils import timezone


class TimestampMixin(models.Model):
    """Agrega timestamps automáticos a cualquier modelo"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """Permite borrado lógico en lugar de físico"""
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def hard_delete(self):
        super().delete()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])


class ActivableMixin(models.Model):
    """Permite activar/desactivar registros"""
    activo = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def activar(self):
        self.activo = True
        self.save(update_fields=['activo'])

    def desactivar(self):
        self.activo = False
        self.save(update_fields=['activo'])
