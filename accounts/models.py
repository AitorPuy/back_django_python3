from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from companies.models import Company

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        # Asignar empresa primary por defecto si no se especifica
        if "codigo_empresa" not in extra_fields:
            try:
                primary_company = Company.objects.get(is_primary=True)
                extra_fields["codigo_empresa"] = primary_company
            except Company.DoesNotExist:
                # Si no existe empresa primary, crear una o usar la primera disponible
                company = Company.objects.first()
                if company:
                    extra_fields["codigo_empresa"] = company
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("user", "User"),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")
    codigo_empresa = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="usuarios",
        verbose_name="Código Empresa",
        null=False,
        blank=False
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
