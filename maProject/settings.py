"""
Django settings for maProject project.
"""

from pathlib import Path
import os
import dj_database_url # Thư viện hỗ trợ Database trên Cloud

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================================================
# 1. CẤU HÌNH BẢO MẬT & MÔI TRƯỜNG
# =========================================================

# SECURITY WARNING: keep the secret key used in production secret!
# (Trên thực tế nên dùng biến môi trường, nhưng để demo ta giữ nguyên)
SECRET_KEY = 'django-insecure-^7-+va&ti_i#8_^=a6c(^8b*w26b6gunrnia@arj3f!zjivzdr'

# Tự động tắt DEBUG khi lên Render (để an toàn), bật DEBUG khi ở máy local
# Logic: Nếu tìm thấy biến 'RENDER' trong môi trường -> False, ngược lại -> True
DEBUG = 'RENDER' not in os.environ

# Cho phép tất cả các host truy cập (Ngrok, Render, Localhost)
ALLOWED_HOSTS = ['*']

# Tin tưởng các nguồn request từ Ngrok và Render (để không bị lỗi CSRF khi đăng nhập)
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
    # App của bạn
    'translate_app',
    'rest_framework'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    
    # [QUAN TRỌNG] Whitenoise giúp phục vụ file tĩnh trên Server Linux/Render
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
        'DIRS': [BASE_DIR / 'templates'], # Đảm bảo trỏ đúng thư mục templates gốc
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
# 3. CẤU HÌNH DATABASE (TỰ ĐỘNG CHUYỂN ĐỔI)
# =========================================================

# Logic: Nếu có biến môi trường DATABASE_URL (tức là đang ở trên Render) thì dùng Postgres
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
else:
    # Nếu không (đang ở máy Local), dùng MySQL XAMPP của bạn
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'mywebsite',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': '127.0.0.1',
            'PORT': '3307', # Port MySQL của bạn
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
        }
    }


#Password validation
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
# 4. STATIC & MEDIA FILES (QUAN TRỌNG KHI DEPLOY)
# =========================================================

# URL để truy cập file tĩnh
STATIC_URL = 'static/'

# Nơi gom file tĩnh khi chạy lệnh collectstatic (Render cần cái này)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Thư mục chứa file tĩnh trong quá trình phát triển
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Cấu hình nén file tĩnh cho Whitenoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Cấu hình Media (File upload từ người dùng)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'