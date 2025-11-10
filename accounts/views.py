from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .serializers import (
    UserSerializer,
    RegisterSerializer,
    ProfileUpdateSerializer,
    PasswordChangeSerializer,
)
from .permissions import IsAdmin, IsSelfOrAdmin

User = get_user_model()

# Auth por email (JWT)
class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        return token

    # forzar email como campo de login
    username_field = User.EMAIL_FIELD if hasattr(User, "EMAIL_FIELD") else "email"

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer

# Registro público
class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

# Perfil propio + cambio de contraseña (sin DELETE)
class MeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # /accounts/me/  -> GET
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        # /accounts/me/  -> PATCH
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)

    def update(self, request, pk=None):
        # /accounts/me/  -> PUT
        serializer = ProfileUpdateSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=["post"], url_path="change-password")
    def change_password(self, request):
        s = PasswordChangeSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        user = request.user
        user.set_password(s.validated_data["new_password"])
        user.save()
        return Response({"detail": "Contraseña cambiada."}, status=status.HTTP_200_OK)

# Administración completa de usuarios (incluye DELETE, activar/desactivar, cambiar rol)
class UserAdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    @action(detail=True, methods=["post"], url_path="set-role")
    def set_role(self, request, pk=None):
        user = self.get_object()
        role = request.data.get("role")
        if role not in ["admin", "user"]:
            return Response({"role": "Valor inválido."}, status=status.HTTP_400_BAD_REQUEST)
        user.role = role
        user.save()
        return Response(UserSerializer(user).data)

    @action(detail=True, methods=["post"], url_path="set-active")
    def set_active(self, request, pk=None):
        user = self.get_object()
        value = request.data.get("is_active")
        if str(value).lower() not in ["true", "false"]:
            return Response({"is_active": "Usa true/false."}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = str(value).lower() == "true"
        user.save()
        return Response(UserSerializer(user).data)
