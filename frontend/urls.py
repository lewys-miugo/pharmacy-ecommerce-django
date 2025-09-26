from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    # Public pages
    path('', views.HomeView.as_view(), name='home'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # User authentication
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # Customer order pages
    path('cart/', views.CartView.as_view(), name='cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('orders/', views.UserOrderListView.as_view(), name='user_orders'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    
    # Admin CRUD pages
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    
    # Category CRUD
    path('admin/categories/', views.CategoryListView.as_view(), name='category_list'),
    path('admin/categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('admin/categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('admin/categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # Product CRUD
    path('admin/products/', views.AdminProductListView.as_view(), name='admin_product_list'),
    path('admin/products/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('admin/products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('admin/products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # Order management
    path('admin/orders/', views.AdminOrderListView.as_view(), name='admin_order_list'),
    path('admin/orders/<int:pk>/', views.AdminOrderDetailView.as_view(), name='admin_order_detail'),
    path('admin/orders/<int:pk>/update-status/', views.OrderStatusUpdateView.as_view(), name='order_status_update'),
]