from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_initial_article(sender, **kwargs):
    """Crea un registro inicial si la tabla está vacía"""
    from .models import Article
    if Article.objects.count() == 0:
        Article.objects.create(name="Mi Artículo")


class ArticlesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'articles'

    def ready(self):
        post_migrate.connect(create_initial_article, sender=self)
