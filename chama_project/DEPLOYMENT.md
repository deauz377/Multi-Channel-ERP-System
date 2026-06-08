# Chama Management System - Deployment Guide

## Production Deployment

This guide covers deploying the Chama Management System to a production environment.

## Prerequisites

- Ubuntu 20.04+ server or similar Linux distribution
- Python 3.10+
- PostgreSQL 12+
- Nginx or Apache web server
- Supervisor or Systemd for process management
- SSL certificate (Let's Encrypt recommended)

## Environment Setup

### 1. System Packages

```bash
sudo apt update
sudo apt install python3-pip python3-venv postgresql postgresql-contrib nginx supervisor
```

### 2. Create Application User

```bash
sudo useradd -m -s /bin/bash chama
sudo su - chama
```

### 3. Clone/Copy Project

```bash
git clone <repository-url> chama_project
cd chama_project
```

### 4. Setup Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Database Configuration

### 1. Create PostgreSQL Database

```bash
sudo -u postgres psql
CREATE DATABASE chama_db;
CREATE USER chama_user WITH PASSWORD 'strong_password_here';
ALTER ROLE chama_user SET client_encoding TO 'utf8';
ALTER ROLE chama_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE chama_user SET default_transaction_deferrable TO on;
ALTER ROLE chama_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE chama_db TO chama_user;
\q
```

### 2. Update Settings

Create `.env` file in project root:

```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://chama_user:strong_password_here@localhost:5432/chama_db
```

Update `chama_config/settings.py`:

```python
from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')
SECRET_KEY = config('SECRET_KEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='chama_db'),
        'USER': config('DB_USER', default='chama_user'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```

### 3. Run Migrations

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

## Web Server Configuration

### Gunicorn Setup

Install Gunicorn:
```bash
pip install gunicorn
```

Create socket file location:
```bash
sudo mkdir -p /run/gunicorn
sudo chown chama:chama /run/gunicorn
```

### Systemd Service

Create `/etc/systemd/system/chama.service`:

```ini
[Unit]
Description=Chama Management System Gunicorn Application
After=network.target

[Service]
User=chama
Group=www-data
WorkingDirectory=/home/chama/chama_project
ExecStart=/home/chama/chama_project/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/run/gunicorn/chama.sock \
    chama_config.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable chama
sudo systemctl start chama
sudo systemctl status chama
```

### Nginx Configuration

Create `/etc/nginx/sites-available/chama`:

```nginx
upstream chama {
    server unix:/run/gunicorn/chama.sock fail_timeout=0;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    client_max_body_size 10M;

    location /static/ {
        alias /home/chama/chama_project/staticfiles/;
    }

    location /media/ {
        alias /home/chama/chama_project/media/;
    }

    location / {
        proxy_pass http://chama;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/chama /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL Certificate with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com
```

Auto-renewal:
```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## Firewall Configuration

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Backup Strategy

### Database Backup

Create `/home/chama/backup_db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/chama/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/chama_db_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR
pg_dump -U chama_user chama_db > $BACKUP_FILE
gzip $BACKUP_FILE

# Keep last 30 days of backups
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

Add to crontab:
```bash
crontab -e
0 2 * * * /home/chama/backup_db.sh
```

## Monitoring and Logging

### Django Logging

Add to settings.py:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/home/chama/logs/chama.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### Monitoring Services

Install Prometheus and Grafana for monitoring application metrics.

## Performance Optimization

1. **Database Indexing**: Add indexes on frequently queried fields
2. **Caching**: Implement Redis for caching
3. **CDN**: Use CDN for static files
4. **Database Connection Pooling**: Use PgBouncer for PostgreSQL
5. **Async Tasks**: Use Celery for background tasks

## Troubleshooting

### Service Not Starting

```bash
sudo journalctl -u chama -n 50
sudo systemctl restart chama
```

### Database Connection Issues

```bash
sudo -u postgres psql
\l  # List databases
\du # List users
```

### Nginx Issues

```bash
sudo nginx -t
sudo journalctl -u nginx -n 50
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Regular security updates: `sudo apt update && sudo apt upgrade`
- [ ] Implement rate limiting
- [ ] Enable CSRF protection (enabled by default)
- [ ] Use strong SECRET_KEY
- [ ] Disable DEBUG in production
- [ ] Configure allowed hosts
- [ ] Setup monitoring and alerts
- [ ] Regular backups
- [ ] Review application logs regularly

## Maintenance

### Update Dependencies

```bash
pip list --outdated
pip install --upgrade package_name
pip install -r requirements.txt --upgrade
```

### Database Optimization

```bash
python manage.py shell
>>> from django.db import connection
>>> connection.cursor().execute("VACUUM ANALYZE;")
```

### Clean Old Sessions

```bash
python manage.py clearsessions
```

## Support

For deployment issues or questions, contact your system administrator or the development team.
