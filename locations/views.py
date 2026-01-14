import os
import requests
from django.conf import settings
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from openai import OpenAI

from .serializers import (
    LocationRequestSerializer,
    LocationResponseSerializer,
    GenerateDescriptionRequestSerializer,
    GenerateDescriptionResponseSerializer,
)


class GetCityNameView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LocationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        latitude = serializer.validated_data["latitude"]
        longitude = serializer.validated_data["longitude"]
        google_api_key = os.getenv("GOOGLE_GEOCODING_API_KEY")

        if not google_api_key:
            return Response(
                {"error": "Google Geocoding API key not configured"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            # Llamar a Google Geocoding API
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                "latlng": f"{latitude},{longitude}",
                "key": google_api_key,
                "language": "es",
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data["status"] != "OK" or not data.get("results"):
                return Response(
                    {"error": "No se pudo obtener la ubicación"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Extraer el nombre de la ciudad/población
            result = data["results"][0]
            formatted_address = result.get("formatted_address", "")
            city_name = formatted_address

            # Intentar obtener el nombre de la ciudad desde los componentes
            for component in result.get("address_components", []):
                types = component.get("types", [])
                if "locality" in types:
                    city_name = component.get("long_name", city_name)
                    break
                elif "administrative_area_level_2" in types and city_name == formatted_address:
                    city_name = component.get("long_name", city_name)

            response_serializer = LocationResponseSerializer(
                {"city_name": city_name, "formatted_address": formatted_address}
            )
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Response(
                {"error": f"Error al conectar con Google API: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"error": f"Error inesperado: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GenerateDescriptionView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GenerateDescriptionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        city_name = serializer.validated_data["city_name"]
        topic = serializer.validated_data["topic"]
        openai_api_key = os.getenv("OPENAI_API_KEY")

        if not openai_api_key:
            return Response(
                {"error": "OpenAI API key not configured"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            # Inicializar cliente OpenAI con api_key como parámetro
            client = OpenAI(api_key=openai_api_key)
            
            # Crear el prompt para OpenAI
            prompt = f"Escribe una frase corta (máximo 40 caracteres) sobre {city_name} relacionada con {topic}. La frase debe ser informativa y concisa."

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente que genera descripciones breves y precisas sobre lugares.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=50,
                temperature=0.7,
            )

            description = response.choices[0].message.content.strip()

            # Asegurar que no supere los 40 caracteres
            if len(description) > 40:
                description = description[:37] + "..."

            response_serializer = GenerateDescriptionResponseSerializer(
                {"description": description}
            )
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = str(e)
            error_str_lower = error_message.lower()
            
            # Manejar errores específicos de OpenAI
            if "insufficient_quota" in error_str_lower or "429" in error_message:
                error_message = (
                    "Tu cuenta de OpenAI ha excedido la cuota disponible o tiene problemas de facturación. "
                    "Por favor, verifica tu plan y método de pago en https://platform.openai.com/account/billing"
                )
            elif "invalid api key" in error_str_lower or "401" in error_message or "authentication" in error_str_lower:
                error_message = (
                    "La API key de OpenAI no es válida o ha sido revocada. "
                    "Verifica que la clave en el archivo .env coincida con la de tu dashboard: "
                    "https://platform.openai.com/api-keys"
                )
            elif "insufficient_quota" in error_str_lower:
                error_message = (
                    "Tu cuenta de OpenAI ha excedido la cuota disponible. "
                    "Verifica tu plan y método de pago en https://platform.openai.com/account/billing"
                )
            
            response_data = {"error": error_message}
            if settings.DEBUG:
                response_data["raw_error"] = str(e)
            
            return Response(
                response_data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
