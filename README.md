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

## Local Development Setup

### Prerequisites
- Docker and Docker Compose installed
- Git installed

### Step-by-Step Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd django-ecommerce
   ```

2. **Copy environment variables:**
   ```bash
   cp .env.example .env
   ```

3. **Start the services:**
   ```bash
   docker compose up -d
   ```

4. **Wait for services to be ready** (about 30-60 seconds), then check logs:
   ```bash
   docker compose logs web
   ```

5. **Access the application:**
   - Frontend: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin/

### Test User Accounts

The seeder creates the following test accounts for you to use:

#### Super Admin Account
- **Username:** `admin`
- **Password:** `admin123`
- **Email:** `admin@pharmacy.com`
- **Access:** Full admin access, can manage all products, categories, and orders

#### Customer Account
- **Username:** `customer`
- **Password:** `customer123`
- **Email:** `customer@pharmacy.com`
- **Access:** Can browse products, add to cart, place orders

#### Test User Account
- **Username:** `testuser`
- **Password:** `test123`
- **Email:** `test@pharmacy.com`
- **Access:** Customer account for testing functionalities

### Testing the Application

1. **Admin Functions:**
   - Login with admin credentials at http://localhost:8000/admin/
   - Manage products, categories, and view orders
   - Access admin dashboard at http://localhost:8000/

2. **Customer Functions:**
   - Login with customer/testuser credentials
   - Browse products and categories
   - Add items to cart and place orders
   - View order history

3. **API Endpoints:**
   - Health check: http://localhost:8000/api/health/
   - Categories: http://localhost:8000/api/categories/
   - Products: http://localhost:8000/api/products/
   - Orders: http://localhost:8000/api/orders/ (requires authentication)

### Development Commands

```bash
# View logs
docker compose logs -f web

# Run migrations
docker compose exec web python manage.py migrate

# Create superuser (if needed)
docker compose exec web python manage.py createsuperuser

# Run tests
docker compose exec web python manage.py test

# Access Django shell
docker compose exec web python manage.py shell

# Reseed database
docker compose exec web python manage.py seed_data

# Stop services
docker compose down

# Rebuild and restart
docker compose down
docker compose up --build
```

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

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   docker compose down
   docker compose up
   ```

2. **Database connection issues:**
   ```bash
   docker compose down -v  # Remove volumes
   docker compose up --build
   ```

3. **Permission denied on build.sh:**
   ```bash
   chmod +x build.sh
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License
