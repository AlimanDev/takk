import os
from pathlib import Path
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from corsheaders.defaults import default_headers
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(', ')
# Cors setting
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    'accept-language',
]
# CORS_ALLOWED_ORIGINS = ['*']
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DB_NAME', 'takk'),
        'USER': os.getenv('DB_USER', 'takk'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'takk'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

MEDIA_ROOT = (os.path.join(BASE_DIR, 'media'))
MEDIA_URL = "/media/"

STATIC_URL = '/static/'
STATIC_ROOT = Path(BASE_DIR).joinpath('static')
# STATICFILES_DIRS = [Path(BASE_DIR).joinpath('static')]

# GDAL_LIBRARY_PATH = '/home/user/takk/local/lib/libgdal.so'

sentry_sdk.init(
    dsn=os.getenv('SENTRY_KEY'),
    integrations=[DjangoIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

from conf.settings.base import *