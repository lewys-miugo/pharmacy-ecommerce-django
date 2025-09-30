from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('api/health/', health_check, name='health'),
    path('api/', include('categories.urls')),
    path('api/', include('products.urls')),
    path('api/', include('orders.urls')),
    path('', include('frontend.urls')),
]
