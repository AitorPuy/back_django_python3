from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from accounts.permissions import IsAdmin
from .models import Company
from .serializers import CompanySerializer

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAdmin]

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


@api_view(['GET'])
@permission_classes([])  # Endpoint público, sin autenticación
def get_primary_company(request):
    """Endpoint público para obtener la empresa principal (sin autenticación)"""
    try:
        primary_company = Company.objects.filter(is_primary=True).first()
        if primary_company:
            return Response({
                'id': primary_company.id,
                'name': primary_company.name,
                'is_primary': primary_company.is_primary
            })
        else:
            return Response({
                'name': 'AdminLTE',
                'is_primary': False
            }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'name': 'AdminLTE',
            'is_primary': False
        }, status=status.HTTP_200_OK)
