import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-$e0k^+_4+ixbow#6^y&y09-3pmfkv=a05uzfhz2b#v07-o0l&c'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

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
# # REDIS related settings
# REDIS_HOST = 'localhost'
# REDIS_PORT = '6379'
# BROKER_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
# BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
# CELERY_RESULT_BACKEND = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'

from conf.settings.base import *