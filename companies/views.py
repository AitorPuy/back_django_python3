from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import Company
from .serializers import CompanySerializer

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        # Si se marca como principal, desmarcar los demás
        if instance.is_primary:
            Company.objects.exclude(id=instance.id).update(is_primary=False)

    def perform_update(self, serializer):
        instance = serializer.save()
        # Si se marca como principal, desmarcar los demás
        if instance.is_primary:
            Company.objects.exclude(id=instance.id).update(is_primary=False)
