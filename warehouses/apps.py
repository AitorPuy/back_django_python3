from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_initial_warehouse(sender, **kwargs):
    """Crea un registro inicial si la tabla está vacía"""
    from .models import Warehouse
    if Warehouse.objects.count() == 0:
        Warehouse.objects.create(name="Mi Almacén")


class WarehousesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'warehouses'

    def ready(self):
        post_migrate.connect(create_initial_warehouse, sender=self)
