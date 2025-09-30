from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    display_name = forms.CharField(max_length=100, required=False, help_text='Optional: How you want to be displayed')

    class Meta:
        model = CustomUser
        fields = ("username", "email", "display_name", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.display_name = self.cleaned_data["display_name"]
        if commit:
            user.save()
        return user