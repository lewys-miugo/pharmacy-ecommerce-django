from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'price', 'created_at')
    list_filter = ('categories', 'created_at')
    search_fields = ('name', 'sku')
    filter_horizontal = ('categories',)