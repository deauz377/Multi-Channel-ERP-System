# Chama Management System

A standalone Django-based savings group (Chama) management system with features for tracking member contributions, loans, and payments.

## Features

- **Member Management**: Register and manage group members
- **Contribution Tracking**: Record and track member contributions
- **Loan Management**: Create, approve, and track loans
- **Payment Tracking**: Record loan payments and track payment history
- **Dashboard**: View key statistics and summaries
- **User Authentication**: Secure login with member profiles
- **Admin Interface**: Full Django admin for data management

## Project Structure

```
chama_project/
├── chama_config/          # Django project settings
│   ├── settings.py        # Configuration
│   ├── urls.py           # URL routing
│   ├── wsgi.py           # WSGI application
│   └── asgi.py           # ASGI application
├── chama/                 # Main chama app
│   ├── models.py         # Database models
│   ├── views.py          # View logic
│   ├── forms.py          # Django forms
│   ├── urls.py           # App URL patterns
│   ├── admin.py          # Admin configuration
│   └── migrations/       # Database migrations
├── templates/            # HTML templates
├── manage.py            # Django management script
└── requirements.txt     # Python dependencies
```

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Steps

1. **Navigate to the project directory:**
   ```bash
   cd chama_project
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Unix or MacOS
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (if needed):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the application:**
   - Web Interface: http://localhost:8000/
   - Admin Panel: http://localhost:8000/admin/

## Default Credentials

- **Username**: admin
- **Password**: admin123

*Important: Change these credentials in production!*

## Database Models

### Member
- Represents a member of the savings group
- Fields: name, email, phone, join_date, is_active

### Contribution
- Records member contributions
- Fields: member, amount, date, description, created_at

### Loan
- Tracks loans given to members
- Fields: member, principal, interest, due_date, status, description, created_at, updated_at
- Status choices: pending, approved, active, paid, defaulted

### LoanPayment
- Records individual loan payments
- Fields: loan, amount, payment_date, notes, created_at

## API Endpoints

The system includes REST API endpoints for:
- Member listing and creation
- Contribution management
- Loan management and status updates
- Payment tracking

Access API documentation at: http://localhost:8000/api/

## Configuration

### Settings File (chama_config/settings.py)

Key configurations:
```python
DEBUG = True  # Set to False in production
ALLOWED_HOSTS = ['*']  # Restrict in production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Environment Variables

For production, use environment variables:
```bash
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key-here
```

## Development

### Creating a Superuser
```bash
python manage.py createsuperuser
```

### Running Migrations
```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Running Tests
```bash
python manage.py test
```

## Deployment

For production deployment, see [DEPLOYMENT.md](DEPLOYMENT.md)

Key considerations:
- Use a production WSGI server (Gunicorn, uWSGI)
- Use a production database (PostgreSQL, MySQL)
- Enable HTTPS/SSL
- Configure static and media files
- Set up proper logging
- Use environment variables for sensitive data
- Run `python manage.py collectstatic` for static files

## Troubleshooting

### Database Errors
- Delete `db.sqlite3` and run migrations again
- Check database permissions
- Verify PostgreSQL/MySQL connection if using production database

### Static Files Not Loading
- Run `python manage.py collectstatic`
- Check `STATIC_URL` and `STATIC_ROOT` settings

### Authentication Issues
- Clear browser cookies/cache
- Verify user exists in admin panel
- Check email configuration for password reset

## Support and Contributing

For issues and feature requests, contact the development team.

## License

This project is proprietary software.

## API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Authentication
All API endpoints require authentication using session cookies or tokens.

### Endpoints

#### Members
- `GET /api/members/` - List all members
- `POST /api/members/` - Create new member
- `GET /api/members/{id}/` - Get member details

#### Contributions
- `GET /api/contributions/` - List all contributions
- `POST /api/contributions/` - Record new contribution

#### Loans
- `GET /api/loans/` - List all loans
- `POST /api/loans/` - Create new loan
- `GET /api/loans/{id}/` - Get loan details

#### Payments
- `GET /api/payments/` - List all payments
- `POST /api/payments/` - Record new payment
