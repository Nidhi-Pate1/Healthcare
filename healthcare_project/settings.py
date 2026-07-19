import os
from pathlib import Path
import os
import dj_database_url
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = os.environ.get("DEBUG", "False") == "True"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'healthcare', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'healthcare_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'healthcare_project.wsgi.application'
DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///db.sqlite3",
        conn_max_age=600
    )
}

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#RAZORPAY_KEY_ID = "rzp_test_SgavfrtjQ3giiY"
RAZORPAY_KEY_ID = "rzp_test_T6EnUtBXSMn61h"

#test api key=rzp_test_ShIIoTntS2b5C3
#RAZORPAY_KEY_SECRET = "rd3xPnSvJnWp37uMIt3Y8PQ5"
RAZORPAY_KEY_SECRET = "Dt1GVeHJFxb0AkH7sOkKAyK0"

#test secret key=wYHG3rvKOdhWPbdSc9bKIQsX
LOGIN_URL = '/login/'
import os

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")