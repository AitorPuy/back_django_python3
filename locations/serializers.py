from rest_framework import serializers


class LocationRequestSerializer(serializers.Serializer):
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)


class LocationResponseSerializer(serializers.Serializer):
    city_name = serializers.CharField()
    formatted_address = serializers.CharField(required=False)


class GenerateDescriptionRequestSerializer(serializers.Serializer):
    city_name = serializers.CharField(required=True)
    topic = serializers.ChoiceField(
        choices=["Historia", "Geografía", "Economía"], required=True
    )


class GenerateDescriptionResponseSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=40)
