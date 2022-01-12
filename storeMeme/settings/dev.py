from .common import *

DEBUG = True
SECRET_KEY = 'django-insecure-v__%(*gt-^z)5+dvugv8=p=m2o-&#%_wasl@7m1_73%gy1=w#$'

if DEBUG:
    MIDDLEWARE += [
        'silk.middleware.SilkyMiddleware',
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]
    INSTALLED_APPS += [
        'debug_toolbar',
        'silk',
    ]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'store_meme',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': 'root'
    }
}
