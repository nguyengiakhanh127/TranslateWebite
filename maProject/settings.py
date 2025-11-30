"""
Django settings for maProject project.
"""

from pathlib import Path
import os
import sys  # <--- BẮT BUỘC PHẢI CÓ
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================================================
# 1. CẤU HÌNH BẢO MẬT & MÔI TRƯỜNG
# =========================================================

SECRET_KEY = 'django-insecure-^7-+va&ti_i#8_^=a6c(^8b*w26b6gunrnia@arj3f!zjivzdr'

# Tự động tắt DEBUG khi lên Render
DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.app',
    'https://*.onrender.com',
]

# =========================================================
# 2. ỨNG DỤNG & MIDDLEWARE
# =========================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'translate_app',
    'rest_framework'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'maProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'maProject.wsgi.application'


# =========================================================
# 3. CẤU HÌNH DATABASE (THÔNG MINH)
# =========================================================

# Kiểm tra xem có biến môi trường Render không
if 'DATABASE_URL' in os.environ:
    # 1. Chạy trên Render (Runtime) -> Dùng PostgreSQL
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
elif len(sys.argv) > 0 and sys.argv[1] != 'collectstatic':
    # 2. Chạy Localhost (Dev) -> Dùng MySQL XAMPP
    # (Chỉ khi KHÔNG PHẢI là lệnh collectstatic)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'mywebsite',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': '127.0.0.1',
            'PORT': '3307',
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
        }
    }
else:
    # 3. Chạy lệnh 'collectstatic' (Lúc Build Docker) -> Dùng SQLite
    # (Để tránh lỗi thiếu driver mysqlclient trên Linux)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# =========================================================
# 4. STATIC & MEDIA FILES
# =========================================================

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'