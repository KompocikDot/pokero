"""
Django settings for app project.
Updated/Optimized version.
"""

import os
from pathlib import Path

# Funkcja pomocnicza do bezpiecznego pobierania sekretów
def get_secret(env_var_name: str, file_env_var_name: str = None, default: str = "") -> str:
    # 1. Najpierw spróbuj wczytać z pliku (Docker secrets)
    if file_env_var_name:
        file_path = os.environ.get(file_env_var_name)
        if file_path:
            try:
                with open(file_path) as f:
                    return f.read().strip()
            except IOError:
                pass # Plik nie istnieje, idź dalej
    
    # 2. Jeśli nie ma pliku, spróbuj bezpośrednią zmienną środowiskową
    val = os.environ.get(env_var_name)
    if val:
        return val
    
    # 3. Zwróć wartość domyślną (tylko dla dev/build)
    return default

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
DEBUG = os.environ.get("PRODUCTION") is None

# SECURITY WARNING: keep the secret key used in production secret!
if DEBUG:
    SECRET_KEY = 'django-insecure-test-key-for-local-dev-only'
else:
    # Próbuje wczytać z pliku, a jak nie to ze zmiennej, a na końcu rzuca błąd jeśli puste
    SECRET_KEY = get_secret("SECRET_KEY", "SECRET_KEY_FILE")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY is missing in production!")

ALLOWED_HOSTS = []
if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    allowed_hosts_env = os.environ.get('ALLOWED_HOSTS', '')
    if allowed_hosts_env:
        ALLOWED_HOSTS = allowed_hosts_env.split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tailwind',
    'theme',
    'widget_tweaks',
    'games',
    'tables',
    "comments",
    'csp', # Biblioteka django-csp
    "rules",
    "axes",
]

if DEBUG:
    INSTALLED_APPS += [
        "django_browser_reload",
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Musi być zaraz po SecurityMiddleware
    'csp.middleware.CSPMiddleware',               # Musi być przed generowaniem HTML
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'app.middleware.SecurityHeadersMiddleware', # UWAGA: Wyłącz to, jeśli używasz django-csp i ustawień SECURE_*, żeby nie dublować nagłówków
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]

if DEBUG:
    MIDDLEWARE += [
        "django_browser_reload.middleware.BrowserReloadMiddleware",
    ]

AUTHENTICATION_BACKENDS = (
    'axes.backends.AxesStandaloneBackend',
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'

# Database
# Skonsolidowana logika bazy danych
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ.get('POSTGRES_HOST'),
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': get_secret("POSTGRES_PASSWORD", "POSTGRES_PASSWORD_FILE"),
    }
}

# Dodaj replikę tylko na prawdziwej produkcji, jeśli zdefiniowano host
IS_REAL_PRODUCTION = not DEBUG and os.environ.get('CI') != 'true'
REPLICA_HOST = os.environ.get('POSTGRES_HOST_REPLICA')

if IS_REAL_PRODUCTION and REPLICA_HOST:
    DATABASES['replica'] = DATABASES['default'].copy()
    DATABASES['replica']['HOST'] = REPLICA_HOST
    # Router używamy tylko gdy mamy replikę
    DATABASE_ROUTERS = ['app.db_router.PrimaryReplicaRouter']


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "tables_list_view"
LOGOUT_REDIRECT_URL = "home"

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

# Konfiguracja WhiteNoise (dla Django 4.2+)
# To zapewnia kompresję i cacheowanie plików statycznych
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
TAILWIND_APP_NAME = "theme"

# --- SECURITY & HTTPS ---
if not DEBUG:
    # Cookies & SSL
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Wyjątki dla CI/CD
    if os.environ.get('CI') == 'true':
        SECURE_SSL_REDIRECT = False
        SESSION_COOKIE_SECURE = False
        CSRF_COOKIE_SECURE = False
        SECURE_HSTS_SECONDS = 0
        SECURE_PROXY_SSL_HEADER = None

    # Site Isolation (Spectre) - wymagane oba nagłówki
    SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
    SECURE_CROSS_ORIGIN_EMBEDDER_POLICY = 'require-corp' # Dodane dla pełnej ochrony

    # --- CSP (Content Security Policy) via django-csp ---
    # Poprawiona składnia - django-csp używa stałych CSP_*, a nie słownika CONTENT_SECURITY_POLICY
    # --- CSP (Content Security Policy) via django-csp v4.0+ ---

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["'self'"],
        "script-src": ["'self'"],
        # unsafe-inline jest potrzebne dla panelu admina Django
        "style-src": ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
        "img-src": [
            "'self'",
            "data:",
            "https://igamingpolska.pl",
            "https://tailwindcss.com"
        ],
        "font-src": ["'self'", "https://fonts.gstatic.com"],
        "connect-src": ["'self'"],
        "frame-src": ["'self'"],
        "object-src": ["'none'"],
        "base-uri": ["'self'"],

        # --- NAPRAWA BŁĘDÓW ZAP ---
        # Te dyrektywy nie dziedziczą po default-src, muszą być jawne:
        "frame-ancestors": ["'self'"],  # Chroni przed Clickjackingiem
        "form-action": ["'self'"],      # Chroni przed przejęciem formularzy
    }
}
CSRF_TRUSTED_ORIGINS = ["https://pokerteki.mom"]
if os.environ.get('CI') == 'true':
    CSRF_TRUSTED_ORIGINS.extend(["http://localhost:8000", "http://127.0.0.1:8000"])

# --- AXES Configuration ---
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = None 
AXES_LOCKOUT_PARAMETERS = ["username", "ip_address"]
AXES_MASK_IP = False
AXES_MASK_USERNAME = False

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
        'axes': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'app': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
