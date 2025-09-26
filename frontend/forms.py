from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.text import slugify
from users.models import CustomUser
from categories.models import Category
from products.models import Product
from orders.models import Order

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    display_name = forms.CharField(max_length=255, required=False)
    is_customer = forms.BooleanField(initial=True, required=False, widget=forms.HiddenInput())
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'display_name', 'password1', 'password2', 'is_customer')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.display_name = self.cleaned_data['display_name']
        user.is_customer = True
        if commit:
            user.save()
        return user

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = Category.objects.all()
        self.fields['parent'].empty_label = "No Parent (Root Category)"
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if not slug:
            slug = slugify(self.cleaned_data.get('name', ''))
        return slug

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['sku', 'name', 'description', 'price', 'categories']
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'categories': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categories'].queryset = Category.objects.all()

class OrderStatusForm(forms.ModelForm):
    STATUS_CHOICES = [
        ('placed', 'Placed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Order
        fields = ['status']

class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 80px;'})
    )