# 5-Minute Quick Start Guide

[← Back to Documentation](../README.md)

---

## 🚀 Get Up and Running in 5 Minutes

This quick start guide will help you get the Enterprise SaaS Backend Foundation running on your local machine in just 5 minutes.

## Prerequisites

Make sure you have:
- Python 3.11+ installed
- pip (Python package manager)
- Git (optional, for cloning)

## Step 1: Get the Code (30 seconds)

### Option A: Clone with Git
```bash
git clone <repository-url> enterprise-foundation
cd enterprise-foundation
```

### Option B: Download ZIP
Download and extract the ZIP file, then:
```bash
cd enterprise-foundation
```

## Step 2: Set Up Environment (1 minute)

### Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

## Step 3: Install Dependencies (2 minutes)

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 4: Quick Configuration (30 seconds)

Create a `.env` file in the project root:

```bash
# Create .env file
echo "SECRET_KEY=quick-start-secret-key-change-in-production" > .env
echo "DEBUG=True" >> .env
```

## Step 5: Initialize Database (30 seconds)

```bash
python manage.py migrate
```

## Step 6: Create Admin User (30 seconds)

```bash
python manage.py createsuperuser
```

When prompted, enter:
- Username: `admin`
- Email: `admin@example.com`
- Password: (choose a secure password)

## Step 7: Run the Server (10 seconds)

```bash
python manage.py runserver
```

## 🎉 Success! You're Running!

Open your browser and visit:

- **Admin Interface**: http://localhost:8000/admin/
  - Login with the credentials you just created
  
- **API Documentation**: http://localhost:8000/api/docs/
  - Interactive API documentation
  
- **Health Check**: http://localhost:8000/api/health/
  - Should return `{"status": "healthy"}`

## What's Next?

### Try These Features:

1. **Create an Organization** (in Admin):
   - Go to Admin → Accounts → Organizations
   - Click "Add Organization"
   - Name: "Test Company"
   - Slug: "test-company"
   - Save

2. **Test the API**:
   ```bash
   # Get auth token
   curl -X POST http://localhost:8000/api/auth/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "your-password"}'
   ```

3. **Create a Test User**:
   ```bash
   python manage.py shell
   >>> from django.contrib.auth.models import User
   >>> User.objects.create_user('testuser', 'test@example.com', 'testpass123')
   >>> exit()
   ```

## Quick Commands Reference

| What You Want | Command |
|--------------|---------|
| Stop the server | `Ctrl+C` |
| Run tests | `pytest` |
| View all URLs | `python manage.py show_urls` |
| Check configuration | `python manage.py check` |
| Access Django shell | `python manage.py shell` |
| View database | `python manage.py dbshell` |

## Troubleshooting

### Port 8000 Already in Use?
```bash
# Run on different port
python manage.py runserver 8080
```

### Missing Dependencies?
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### Database Errors?
```bash
# Reset database (development only!)
rm db.sqlite3
python manage.py migrate
```

### Can't Access Admin?
```bash
# Create new superuser
python manage.py createsuperuser
```

## Next Steps

Now that you have the foundation running:

1. **Read the Full Documentation**:
   - [User Guide](../user-guide/01-introduction.md)
   - [Configuration Guide](../user-guide/03-configuration.md)

2. **Set Up Development Environment**:
   - Install Redis for caching
   - Set up PostgreSQL for production-like environment
   - Configure email settings

3. **Build Your First Feature**:
   - [Building Your First App](./first-app.md)
   - [API Development Guide](../user-guide/08-api-guide.md)

4. **Learn About Security**:
   - [Security Features](../user-guide/07-security.md)
   - Enable MFA for your admin account
   - Set up API keys

## Pro Tips

💡 **Development Tools**:
```bash
# Install helpful development packages
pip install ipython django-extensions django-debug-toolbar

# Use IPython shell
python manage.py shell_plus
```

💡 **Auto-reload on file changes**:
The development server automatically reloads when you change code files.

💡 **API Testing Tool**:
```bash
# Install HTTPie for easier API testing
pip install httpie

# Test API with HTTPie
http GET localhost:8000/api/health/
```

💡 **Database Viewer**:
Use a tool like [DBeaver](https://dbeaver.io/) or [TablePlus](https://tableplus.com/) to view your database.

---

## 🎊 Congratulations!

You've successfully set up the Enterprise SaaS Backend Foundation! You now have a fully functional backend with:

- ✅ User authentication system
- ✅ Admin interface
- ✅ REST API with documentation
- ✅ Multi-tenant architecture ready
- ✅ Security features built-in
- ✅ Analytics and monitoring ready

**Time to build something amazing! 🚀**

---

**Need Help?** Check the [Troubleshooting Guide](../user-guide/14-troubleshooting.md) or [Common Issues](../reference/quick-cards.md#emergency-procedures)

**Last Updated**: January 2024
