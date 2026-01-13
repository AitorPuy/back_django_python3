from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import CompanyViewSet, get_primary_company

router = DefaultRouter()
router.register(r"", CompanyViewSet, basename="companies")

urlpatterns = [
    path("primary/", get_primary_company, name="primary-company"),
] + router.urls
