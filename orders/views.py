from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order

class OrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)
    
    def list(self, request, *args, **kwargs):
        orders = self.get_queryset()
        data = [{'id': o.id, 'total': str(o.total), 'status': o.status} for o in orders]
        return Response(data)