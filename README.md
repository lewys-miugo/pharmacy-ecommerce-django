# Django E-commerce Backend

A Django REST API backend for e-commerce with hierarchical categories, products, orders, and OpenID Connect authentication.

[Live demo](https://pharmacy-ecommerce-django.onrender.com/)

## Features

- Custom user model with customer support
- Hierarchical product categories (unlimited depth)
- Product management with bulk upload
- Order processing with email notifications
- OpenID Connect authentication for customers
- REST API with comprehensive test coverage
- Full frontend with admin CRUD and customer ordering

## Quick Start (Local Development)

1. Clone the repository
2. Copy environment variables: `cp .env.example .env`
3. Start services: `docker compose up -d`
4. Run users migration: `docker compose exec web python manage.py makemigrations users`
5. Run migrations: `docker compose exec web python manage.py migrate`
6. Create superuser: `docker compose exec web python manage.py createsuperuser`
7. Load sample data: `docker compose exec web python manage.py seed_data`

## Deployment on Render

### Prerequisites
- GitHub account
- Render account

### Steps

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Create Render Service:**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name:** `django-ecommerce`
     - **Environment:** `Python`
     - **Build Command:** `./build.sh`
     - **Start Command:** `gunicorn project.wsgi:application`

3. **Add Environment Variables:**
   - `SECRET_KEY`: Generate a secure key
   - `DEBUG`: `False`
   - `RENDER_EXTERNAL_HOSTNAME`: Your Render app URL
   - `DATABASE_URL`: Will be auto-populated when you add PostgreSQL

4. **Add PostgreSQL Database:**
   - In Render Dashboard → "New +" → "PostgreSQL"
   - Name: `ecommerce-db`
   - Link to your web service

5. **Deploy:**
   - Render will automatically deploy when you push to main branch
   - First deployment takes 5-10 minutes

### Post-Deployment

1. **Access your app:** `https://your-app-name.onrender.com`
2. **Admin login:** `admin` / `admin123` (change immediately)
3. **Sample customer:** `customer` / `customer123`

## API Endpoints

- `GET /api/health/` - Health check
- `GET /api/categories/` - List categories
- `GET /api/products/` - List products
- `POST /api/orders/` - Create order (authenticated)

## Frontend Features

### For Super Admin:
- Complete CRUD for Categories and Products
- Order management and status updates
- Dashboard with statistics
- Admin-only access controls

### For Normal Users:
- Product browsing and search
- Shopping cart functionality
- Order placement and tracking
- User registration and authentication

## Testing

Run tests locally:
```bash
docker compose exec web python manage.py test
docker compose exec web pytest --cov=project --cov-report=term-missing
```

## Environment Variables

### Required:
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: PostgreSQL connection string
- `DEBUG`: Set to `False` in production

### Optional:
- `ADMIN_EMAIL`: Admin email address
- `OIDC_RP_CLIENT_ID`: OpenID Connect client ID
- `OIDC_RP_CLIENT_SECRET`: OpenID Connect client secret
- `OIDC_OP_DOMAIN`: OpenID Connect provider domain

## Project Structure

```
├── project/                 # Django project settings
├── users/                   # Custom user model
├── categories/              # Hierarchical categories
├── products/                # Product management
├── orders/                  # Order processing
├── frontend/                # Web interface
├── templates/               # HTML templates
├── static/                  # Static files
├── requirements.txt         # Python dependencies
├── build.sh                 # Render build script
└── render.yaml             # Render configuration
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License
