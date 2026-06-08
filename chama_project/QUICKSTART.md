# Chama Project - Quick Start

## Running the Standalone Chama Project

### Step 1: Install Dependencies
```bash
cd chama_project
pip install -r requirements.txt
```

### Step 2: Run Migrations (if needed)
```bash
python manage.py migrate
```

### Step 3: Create Superuser (if needed)
```bash
python manage.py createsuperuser
```

### Step 4: Start Development Server
```bash
python manage.py runserver 8001
```

The server will run on: **http://localhost:8001/**

Admin panel: **http://localhost:8001/admin/**

## Default Admin Credentials
- **Username**: admin
- **Password**: admin123

⚠️ **Important**: Change these credentials immediately after first login!

## Features Available

### Dashboard
- View key statistics (members, contributions, loans)
- Quick access to common tasks
- Recent contributions and active loans overview

### Member Management
- Register new members
- View member profiles
- Track member contributions and loans

### Contribution Management
- Record member contributions
- View contribution history
- Generate contribution reports

### Loan Management
- Create new loans
- Track loan status (pending, approved, active, paid, defaulted)
- Record loan payments
- Calculate interest automatically

## File Structure

```
chama_project/
├── chama_config/          # Settings & configuration
├── chama/                 # Main application
│   ├── models.py         # Database models
│   ├── views.py          # View handlers
│   ├── forms.py          # Form definitions
│   ├── urls.py           # URL patterns
│   └── admin.py          # Admin configuration
├── templates/            # HTML templates
├── static/              # CSS, JS, Images
├── manage.py            # Django management
├── requirements.txt     # Dependencies
├── README.md           # Full documentation
├── DEPLOYMENT.md       # Production deployment
└── QUICKSTART.md       # This file
```

## Database

The project uses SQLite by default (`db.sqlite3`). For production, use PostgreSQL or MySQL.

## Common Commands

### Create a new member
1. Visit `http://localhost:8001/members/create/`
2. Fill in member details
3. Click Submit

### Record a contribution
1. Go to `http://localhost:8001/contributions/add/`
2. Select member and enter amount
3. Click Submit

### Create a loan
1. Go to `http://localhost:8001/loans/add/`
2. Fill in loan details (principal, interest rate, due date)
3. Click Submit

### Record a payment
1. Go to loan detail page
2. Click "Record Payment"
3. Enter payment amount and date
4. Click Submit

## API Access

REST API endpoints available at:
```
http://localhost:8001/api/
```

## Troubleshooting

### Port Already in Use
```bash
python manage.py runserver 8002  # Use different port
```

### Database Errors
```bash
rm db.sqlite3
python manage.py migrate
```

### Cannot Login
- Check admin credentials in database via admin panel
- Ensure user account is active

## Next Steps

1. Configure email for notifications (optional)
2. Set up backup strategy
3. Plan deployment to production
4. Customize templates and styling
5. Integrate with other systems via API

## Support

For issues or questions:
- Check the full [README.md](README.md)
- Review [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
- Contact the development team

Enjoy using Chama Management System! 🎉
