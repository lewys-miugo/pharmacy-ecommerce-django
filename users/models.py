from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_customer = models.BooleanField(default=False)
    display_name = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return self.display_name or self.username