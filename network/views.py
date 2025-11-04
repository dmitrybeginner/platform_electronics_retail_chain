from rest_framework import viewsets
from .models import NetworkNode
from .serializers import NetworkNodeReadSerializer, NetworkNodeWriteSerializer
from .filters import NetworkNodeFilter
from users.permissions import IsActiveEmployee

class NetworkNodeViewSet(viewsets.ModelViewSet):
    queryset = NetworkNode.objects.select_related('supplier').prefetch_related('products').order_by('created_at')
    filterset_class = NetworkNodeFilter
    permission_classes = [IsActiveEmployee]

    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the request action.
        """
        if self.action in ['list', 'retrieve']:
            return NetworkNodeReadSerializer
        # For 'create', 'update', 'partial_update', 'destroy'
        return NetworkNodeWriteSerializer
