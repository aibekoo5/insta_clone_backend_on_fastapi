# 📷 Instagram-clone on FastAPI

## 📖 Description
An Instagram clone with a Fastapi backend. The application supports authentication, admin role, likes and comments, subscription, history, reels, notification, posts, profile, search.

---

## 🚀 Technologies
- **Python 3.11**
- **FastAPI** - for creating API
- **SQLAlchemy** - for work with database
- **PostgreSQL** - database

---

## ⚙️ Install and run

### 🔧 Cloning a repository
```commandline
git clone https://github.com/USERNAME/REPOSITORY_NAME.git
cd REPOSITORY_NAME
```
### 🐍 Create and activate a virtual environment
```commandline
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```
### 📦 Installing dependencies
```commandline
pip install -r requirements.txt
```
### 🗄️ Setting up Environment Variables
```ini
# Core
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
SECRET_KEY=your_secret_key

# Database Settings (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/db_name

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=user@example.com
SMTP_PASSWORD=password
EMAIL_FROM=user@example.com

# Frontend
FRONTEND_URL=http://localhost:3000

# Password reset
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES=30

# AWS S3 Storage Settings (for media uploads)
AWS_ACCESS_KEY_ID="your_access_id"
AWS_SECRET_ACCESS_KEY="your_secret_key"
AWS_REGION=aws-region (for example: eu-north-1)
S3_BUCKET_NAME=your_s3_bucket_name


# Development/Production Mode
ENVIRONMENT=development

# Rate Limiting (optional)
RATE_LIMIT=100/minute
```
### Perform migrations
```commandline
alembic upgrade head
```
### ️ Run app
```commandline
uvicorn app.main:app --reload
```
### Structure project
```commandline
app/
├── api/
│   ├── admin_user.py
│   ├── auth.py
│   ├── engagement.py
│   ├── follow.py
│   ├── media.py
│   ├── notification.py
│   ├── post.py
│   ├── profile.py
│   ├── search.py
│   └── __init__.py
├── models/
│   ├── comment.py 
│   ├── follow.py
│   ├── like.py
│   ├── notification.py
│   ├── post.py
│   ├── reel.py
│   ├── story.py
│   ├── user.py
│   └── __init__.py
├── schemas/
│   ├── comment.py       
│   ├── notification.py
│   ├── post.py
│   ├── reel.py
│   ├── story.py
│   ├── user.py
│   └── __init__.py
├── services/
│   ├── auth.py    
│   ├── comment.py
│   ├── follow.py
│   ├── like.py
│   ├── notification.py
│   ├── post.py
│   ├── reel.py
│   ├── search.py
│   ├── story.py
│   └── __init__.py
├── utils/
│   ├── file_upload.py      
│   ├── password_reset.py     
│   └── __init__.py
├── main.py       
├── config.py
├── database.py         
├── requirements.txt
└── README.md
```
### In Swagger ui http://127.0.0.1:8000/docs
![img.png](img.png)
![img_1.png](img_1.png)
![img_2.png](img_2.png)
![img_3.png](img_3.png)

### 📝 License
This project is distributed under the MIT license.