from rest_framework import generics
from rest_framework.response import Response
from .models import Product

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    
    def list(self, request, *args, **kwargs):
        products = self.get_queryset()
        data = [{'id': p.id, 'name': p.name, 'price': str(p.price)} for p in products]
        return Response(data)