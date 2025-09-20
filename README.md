# Django E-commerce Backend

A Django REST API backend for e-commerce with hierarchical categories, products, orders, and OpenID Connect authentication.

## Features

- Custom user model with customer support
- Hierarchical product categories (unlimited depth)
- Product management with bulk upload
- Order processing with email notifications
- OpenID Connect authentication for customers
- REST API with comprehensive test coverage

## Quick Start

1. Clone the repository
2. Copy environment variables: `cp .env.example .env`
3. Start services: `docker-compose up -d`
4. Run migrations: `docker-compose exec web python manage.py migrate`
5. Create superuser: `docker-compose exec web python manage.py createsuperuser`
6. Load sample data: `docker-compose exec web python manage.py seed_data`

## API Endpoints

- `GET /api/health/` - Health check
- `GET /api/categories/` - List categories
- `GET /api/products/` - List products
- `POST /api/orders/` - Create order (authenticated)

## Testing

Run tests: `docker-compose exec web python manage.py test`
Run with coverage: `docker-compose exec web pytest --cov=project --cov-report=term-missing`

## Environment Variables

See `.env.example` for required configuration.