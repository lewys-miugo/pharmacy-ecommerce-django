from rest_framework import generics
from rest_framework.response import Response
from .models import Category

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    
    def list(self, request, *args, **kwargs):
        categories = self.get_queryset()
        data = [{'id': cat.id, 'name': cat.name, 'slug': cat.slug} for cat in categories]
        return Response(data)