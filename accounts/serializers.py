from django.contrib.auth import get_user_model, password_validation
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from companies.models import Company

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    codigo_empresa = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    codigo_empresa_nombre = serializers.CharField(source="codigo_empresa.name", read_only=True)
    
    class Meta:
        model = User
        fields = ["id", "email", "role", "is_active", "is_staff", "is_superuser", "first_name", "last_name", "date_joined", "codigo_empresa", "codigo_empresa_nombre"]
        read_only_fields = ["id", "is_staff", "is_superuser", "date_joined", "codigo_empresa_nombre"]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password2 = serializers.CharField(write_only=True, trim_whitespace=False)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(), message=_("Email ya registrado."))]
    )

    class Meta:
        model = User
        fields = ["email", "password", "password2"]

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password2": _("Las contraseñas no coinciden.")})
        password_validation.validate_password(data["password"])
        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password2", None)
        # Asignar empresa primary por defecto si no se especifica
        if "codigo_empresa" not in validated_data:
            try:
                primary_company = Company.objects.get(is_primary=True)
                validated_data["codigo_empresa"] = primary_company
            except Company.DoesNotExist:
                # Si no existe empresa primary, usar la primera disponible o crear una
                company = Company.objects.first()
                if not company:
                    company = Company.objects.create(name="Empresa Principal", is_primary=True)
                validated_data["codigo_empresa"] = company
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, trim_whitespace=False)
    new_password = serializers.CharField(write_only=True, trim_whitespace=False)
    new_password2 = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, data):
        if data["new_password"] != data["new_password2"]:
            raise serializers.ValidationError({"new_password2": _("Las contraseñas no coinciden.")})
        password_validation.validate_password(data["new_password"])
        return data

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("La contraseña actual no es válida."))
        return value
