from django.urls import path
from .views import GetCityNameView, GenerateDescriptionView

urlpatterns = [
    path("get-city-name/", GetCityNameView.as_view(), name="get-city-name"),
    path("generate-description/", GenerateDescriptionView.as_view(), name="generate-description"),
]
