from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.paginator import Paginator
from decimal import Decimal
from django.db import transaction

from products.models import Product
from categories.models import Category
from orders.models import Order, OrderItem
from users.forms import CustomUserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

# Public views
def home(request):
    featured_products = Product.objects.filter(is_active=True)[:8]
    categories = Category.objects.all()[:6]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'frontend/home.html', context)

def product_list(request):
    products = Product.objects.filter(is_active=True)
    category_id = request.GET.get('category')
    search = request.GET.get('search')
    
    if category_id:
        products = products.filter(categories__id=category_id)
    
    if search:
        products = products.filter(name__icontains=search)
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_id,
        'search_query': search,
    }
    return render(request, 'frontend/product_list.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    related_products = Product.objects.filter(
        categories__in=product.categories.all(),
        is_active=True
    ).exclude(id=product_id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'frontend/product_detail.html', context)

# Authentication views
def user_login(request):
    if request.user.is_authenticated:
        return redirect('frontend:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.display_name or user.username}!')
                next_url = request.GET.get('next', 'frontend:home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please provide both username and password.')
    
    return render(request, 'frontend/auth/login.html')

def user_register(request):
    if request.user.is_authenticated:
        return redirect('frontend:home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created successfully for {user.username}! You can now log in.')
            return redirect('frontend:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'frontend/auth/register.html', {'form': form})

def user_logout(request):
    if request.user.is_authenticated:
        username = request.user.display_name or request.user.username
        logout(request)
        messages.success(request, f'Goodbye {username}! You have been logged out successfully.')
    return redirect('frontend:home')

# Cart and checkout views (no login required)
def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = Decimal('0.00')
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            subtotal = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal
        except Product.DoesNotExist:
            # Remove invalid product from cart
            del cart[product_id]
            request.session['cart'] = cart
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'frontend/cart.html', context)

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > product.stock_quantity:
        messages.error(request, f'Only {product.stock_quantity} items available in stock.')
        return redirect('frontend:product_detail', product_id=product_id)
    
    # Get or create cart in session
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart[product_id_str] += quantity
    else:
        cart[product_id_str] = quantity
    
    # Check if total quantity exceeds stock
    if cart[product_id_str] > product.stock_quantity:
        cart[product_id_str] = product.stock_quantity
        messages.warning(request, f'Cart updated to maximum available quantity: {product.stock_quantity}')
    
    request.session['cart'] = cart
    messages.success(request, f'{product.name} added to cart!')
    return redirect('frontend:product_detail', product_id=product_id)

@require_POST
def update_cart(request):
    cart = request.session.get('cart', {})
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 0))
    
    if quantity <= 0:
        if product_id in cart:
            del cart[product_id]
            messages.success(request, 'Item removed from cart.')
    else:
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            if quantity > product.stock_quantity:
                quantity = product.stock_quantity
                messages.warning(request, f'Quantity adjusted to available stock: {quantity}')
            cart[product_id] = quantity
        except Product.DoesNotExist:
            messages.error(request, 'Product not found.')
    
    request.session['cart'] = cart
    return redirect('frontend:cart')

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Your cart is empty.')
        return redirect('frontend:cart')
    
    if request.method == 'POST':
        # Get customer info (required for all orders)
        customer_email = request.POST.get('customer_email')
        customer_name = request.POST.get('customer_name')
        
        if not customer_email or not customer_name:
            messages.error(request, 'Please provide your name and email address.')
            return redirect('frontend:checkout')
        
        with transaction.atomic():
            # Create order
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                status='pending',
                total_amount=Decimal('0.00'),
                guest_email=customer_email if not request.user.is_authenticated else None,
                guest_name=customer_name if not request.user.is_authenticated else None
            )
            
            total_amount = Decimal('0.00')
            
            for product_id, quantity in cart.items():
                try:
                    product = Product.objects.get(id=product_id, is_active=True)
                    
                    # Check stock availability
                    if product.stock_quantity < quantity:
                        messages.error(request, f'Insufficient stock for {product.name}. Only {product.stock_quantity} available.')
                        order.delete()
                        return redirect('frontend:cart')
                    
                    # Create order item
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price
                    )
                    
                    # Reduce stock
                    product.stock_quantity -= quantity
                    product.save()
                    total_amount += order_item.price * order_item.quantity
                    
                except Product.DoesNotExist:
                    continue
            
            # Update order total
            order.total_amount = total_amount
            order.save()
            
            # Clear cart
            request.session['cart'] = {}
            
            messages.success(request, f'Order #{order.id} placed successfully!')
            return redirect('frontend:order_confirmation', order_id=order.id)
    
    # Calculate cart total for display
    cart_items = []
    total = Decimal('0.00')
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            subtotal = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal
        except Product.DoesNotExist:
            continue
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'frontend/checkout.html', context)

def order_confirmation(request, order_id):
    """Order confirmation page for both authenticated and guest users"""
    order = get_object_or_404(Order, id=order_id)
    
    # Allow access if user owns the order or it's a guest order from same session
    if request.user.is_authenticated and order.user == request.user:
        pass  # User owns the order
    elif not order.user and request.session.get('last_order_id') == order.id:
        pass  # Guest order from same session
    else:
        messages.error(request, 'Order not found.')
        return redirect('frontend:home')
    
    # Store order ID in session for guest users
    if not request.user.is_authenticated:
        request.session['last_order_id'] = order.id
    
    return render(request, 'frontend/order_confirmation.html', {'order': order})

# User order views (login required)
@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'frontend/user_orders.html', {'page_obj': page_obj})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'frontend/order_detail.html', {'order': order})

# Admin views (login required, no role restrictions)
@login_required
def admin_dashboard(request):
    stats = {
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'total_customers': User.objects.filter(is_customer=True).count(),
        'low_stock_products': Product.objects.filter(stock_quantity__lt=10).count(),
    }
    
    recent_orders = Order.objects.order_by('-created_at')[:5]
    low_stock_products = Product.objects.filter(stock_quantity__lt=10)[:5]
    
    context = {
        'stats': stats,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'frontend/admin_dashboard.html', context)

@login_required
def admin_products(request):
    products = Product.objects.all().order_by('-created_at')
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'frontend/admin_products.html', {'page_obj': page_obj})

@login_required
def admin_product_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        sku = request.POST.get('sku')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock_quantity = request.POST.get('stock_quantity')
        category_ids = request.POST.getlist('categories')
        
        product = Product.objects.create(
            name=name,
            sku=sku,
            description=description,
            price=Decimal(price),
            stock_quantity=int(stock_quantity)
        )
        
        if category_ids:
            categories = Category.objects.filter(id__in=category_ids)
            product.categories.set(categories)
        
        messages.success(request, f'Product "{product.name}" created successfully!')
        return redirect('frontend:admin_products')
    
    categories = Category.objects.all()
    return render(request, 'frontend/admin_product_form.html', {
        'categories': categories,
        'action': 'Create'
    })

@login_required
def admin_product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.sku = request.POST.get('sku')
        product.description = request.POST.get('description')
        product.price = Decimal(request.POST.get('price'))
        product.stock_quantity = int(request.POST.get('stock_quantity'))
        product.is_active = 'is_active' in request.POST
        product.save()
        
        category_ids = request.POST.getlist('categories')
        if category_ids:
            categories = Category.objects.filter(id__in=category_ids)
            product.categories.set(categories)
        
        messages.success(request, f'Product "{product.name}" updated successfully!')
        return redirect('frontend:admin_products')
    
    categories = Category.objects.all()
    return render(request, 'frontend/admin_product_form.html', {
        'product': product,
        'categories': categories,
        'action': 'Edit'
    })

@login_required
def admin_product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('frontend:admin_products')
    
    return render(request, 'frontend/admin_product_delete.html', {'product': product})

@login_required
def admin_categories(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'frontend/admin_categories.html', {'categories': categories})

@login_required
def admin_category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        description = request.POST.get('description', '')
        
        category = Category.objects.create(
            name=name,
            slug=slug,
            description=description
        )
        
        messages.success(request, f'Category "{category.name}" created successfully!')
        return redirect('frontend:admin_categories')
    
    return render(request, 'frontend/admin_category_form.html', {'action': 'Create'})

@login_required
def admin_category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.slug = request.POST.get('slug')
        category.description = request.POST.get('description', '')
        category.save()
        
        messages.success(request, f'Category "{category.name}" updated successfully!')
        return redirect('frontend:admin_categories')
    
    return render(request, 'frontend/admin_category_form.html', {
        'category': category,
        'action': 'Edit'
    })

@login_required
def admin_category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        return redirect('frontend:admin_categories')
    
    return render(request, 'frontend/admin_category_delete.html', {'category': category})

@login_required
def admin_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    status_choices = Order.STATUS_CHOICES
    
    return render(request, 'frontend/admin_orders.html', {
        'page_obj': page_obj,
        'status_choices': status_choices,
        'current_status': status_filter
    })

@login_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated to {order.get_status_display()}!')
    
    return render(request, 'frontend/admin_order_detail.html', {
        'order': order,
        'status_choices': Order.STATUS_CHOICES
    })