from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'display_name', 'is_customer', 'is_staff')
    list_filter = ('is_customer', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Customer Info', {'fields': ('is_customer', 'display_name')}),
    )