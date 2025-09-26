from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, 
    UpdateView, DeleteView, FormView
)
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.db.models import Q
from decimal import Decimal
import json

from users.models import CustomUser
from categories.models import Category
from products.models import Product
from orders.models import Order, OrderItem
from .forms import (
    CustomUserCreationForm, CategoryForm, ProductForm, 
    OrderStatusForm, AddToCartForm
)

class SuperAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser

# Public Views
class HomeView(TemplateView):
    template_name = 'frontend/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.all()[:6]
        context['categories'] = Category.objects.filter(level=1)
        return context

class ProductListView(ListView):
    model = Product
    template_name = 'frontend/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.all()
        category_id = self.request.GET.get('category')
        search = self.request.GET.get('search')
        
        if category_id:
            queryset = queryset.filter(categories__id=category_id)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category')
        context['search_query'] = self.request.GET.get('search', '')
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'frontend/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_to_cart_form'] = AddToCartForm()
        return context

# Authentication Views
class LoginView(AuthLoginView):
    template_name = 'frontend/auth/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse_lazy('frontend:admin_dashboard')
        return reverse_lazy('frontend:home')

class LogoutView(AuthLogoutView):
    next_page = 'frontend:home'

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'frontend/auth/register.html'
    success_url = reverse_lazy('frontend:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully! Please log in.')
        return response

# Customer Views
class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'frontend/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('cart', {})
        cart_items = []
        total = Decimal('0.00')
        
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                subtotal = product.price * quantity
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'subtotal': subtotal
                })
                total += subtotal
            except Product.DoesNotExist:
                pass
        
        context['cart_items'] = cart_items
        context['total'] = total
        return context
    
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        product_id = request.POST.get('product_id')
        
        cart = request.session.get('cart', {})
        
        if action == 'add':
            quantity = int(request.POST.get('quantity', 1))
            cart[product_id] = cart.get(product_id, 0) + quantity
            messages.success(request, 'Product added to cart!')
        elif action == 'remove':
            cart.pop(product_id, None)
            messages.success(request, 'Product removed from cart!')
        elif action == 'update':
            quantity = int(request.POST.get('quantity', 0))
            if quantity > 0:
                cart[product_id] = quantity
            else:
                cart.pop(product_id, None)
        
        request.session['cart'] = cart
        return redirect('frontend:cart')

class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'frontend/checkout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('cart', {})
        cart_items = []
        total = Decimal('0.00')
        
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                subtotal = product.price * quantity
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'subtotal': subtotal
                })
                total += subtotal
            except Product.DoesNotExist:
                pass
        
        context['cart_items'] = cart_items
        context['total'] = total
        return context
    
    def post(self, request, *args, **kwargs):
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, 'Your cart is empty!')
            return redirect('frontend:cart')
        
        # Create order
        total = Decimal('0.00')
        order = Order.objects.create(
            customer=request.user,
            total=total,
            status='placed'
        )
        
        # Create order items
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                subtotal = product.price * quantity
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price
                )
                total += subtotal
            except Product.DoesNotExist:
                pass
        
        # Update order total
        order.total = total
        order.save()
        
        # Clear cart
        request.session['cart'] = {}
        
        messages.success(request, f'Order #{order.id} placed successfully!')
        return redirect('frontend:order_detail', pk=order.id)

class UserOrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'frontend/user_orders.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).order_by('-created_at')

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'frontend/order_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Order.objects.all()
        return Order.objects.filter(customer=self.request.user)

# Admin Views
class AdminDashboardView(SuperAdminRequiredMixin, TemplateView):
    template_name = 'frontend/admin/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_products'] = Product.objects.count()
        context['total_categories'] = Category.objects.count()
        context['total_orders'] = Order.objects.count()
        context['recent_orders'] = Order.objects.order_by('-created_at')[:5]
        return context

# Category CRUD
class CategoryListView(SuperAdminRequiredMixin, ListView):
    model = Category
    template_name = 'frontend/admin/category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(SuperAdminRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'frontend/admin/category_form.html'
    success_url = reverse_lazy('frontend:category_list')

class CategoryUpdateView(SuperAdminRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'frontend/admin/category_form.html'
    success_url = reverse_lazy('frontend:category_list')

class CategoryDeleteView(SuperAdminRequiredMixin, DeleteView):
    model = Category
    template_name = 'frontend/admin/category_confirm_delete.html'
    success_url = reverse_lazy('frontend:category_list')

# Product CRUD
class AdminProductListView(SuperAdminRequiredMixin, ListView):
    model = Product
    template_name = 'frontend/admin/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

class ProductCreateView(SuperAdminRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'frontend/admin/product_form.html'
    success_url = reverse_lazy('frontend:admin_product_list')

class ProductUpdateView(SuperAdminRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'frontend/admin/product_form.html'
    success_url = reverse_lazy('frontend:admin_product_list')

class ProductDeleteView(SuperAdminRequiredMixin, DeleteView):
    model = Product
    template_name = 'frontend/admin/product_confirm_delete.html'
    success_url = reverse_lazy('frontend:admin_product_list')

# Order Management
class AdminOrderListView(SuperAdminRequiredMixin, ListView):
    model = Order
    template_name = 'frontend/admin/order_list.html'
    context_object_name = 'orders'
    paginate_by = 20
    
    def get_queryset(self):
        return Order.objects.order_by('-created_at')

class AdminOrderDetailView(SuperAdminRequiredMixin, DetailView):
    model = Order
    template_name = 'frontend/admin/order_detail.html'
    context_object_name = 'order'

class OrderStatusUpdateView(SuperAdminRequiredMixin, UpdateView):
    model = Order
    form_class = OrderStatusForm
    template_name = 'frontend/admin/order_status_form.html'
    
    def get_success_url(self):
        return reverse('frontend:admin_order_detail', kwargs={'pk': self.object.pk})