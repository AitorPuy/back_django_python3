from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_initial_company(sender, **kwargs):
    """Crea un registro inicial si la tabla está vacía"""
    from .models import Company
    if Company.objects.count() == 0:
        Company.objects.create(name="Mi Empresa")


class CompaniesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'companies'

    def ready(self):
        post_migrate.connect(create_initial_company, sender=self)
