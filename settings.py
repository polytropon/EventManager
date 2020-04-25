# -*- coding: utf-8 -*-
# https://github.com/divio/aldryn-addons/blob/master/aldryn_addons/urls.py

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

INSTALLED_ADDONS = [
    # <INSTALLED_ADDONS>  # Warning: text inside the INSTALLED_ADDONS tags is auto-generated. Manual changes will be overwritten.
    'aldryn-addons',
    'aldryn-django',
    'aldryn-sso',
    'aldryn-celery',
    # </INSTALLED_ADDONS>
]

import aldryn_addons.settings
aldryn_addons.settings.load(locals())
# all django settings can be altered here
# import os
# MEDIA_ROOT = os.path.join(BASE_DIR,'/media/')
# MEDIA_URL = '/media/'
# LANGUAGE_CODE = 'de-de'
INSTALLED_APPS.extend([
    'crm.apps.CrmConfig',
    'easy_thumbnails',
    'filer',
    'mptt',
    'django_extensions',
    'widget_tweaks',
    'adminsortable',
    # 'channels'
#    'django_memcached'
    'tasks_app',
    # 'django_otp',
    # 'django_otp.plugins.otp_static',
    # 'django_otp.plugins.otp_totp',
    # 'two_factor',
    ])

INSTALLED_APPS.insert(INSTALLED_APPS.index('django.contrib.admin'),'dal')
INSTALLED_APPS.insert(INSTALLED_APPS.index('django.contrib.admin'),'dal_select2')

# MIDDLEWARE.extend(['django.contrib.auth.middleware.AuthenticationMiddleware',
# 'django_otp.middleware.OTPMiddleware'])

# LOGIN_URL = 'two_factor:login'
GRAPH_MODELS = {
  'all_applications': True,
  'group_models': True,
} ## https://django-extensions.readthedocs.io/en/latest/graph_models.html
TIME_ZONE = "Europe/Berlin"

import os
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # ...
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        # ...
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

CSRF_COOKIE_HTTPONLY = False

STATIC_URL = '/static/'
#THUMBNAIL_HIGH_RESOLUTION = True ## https://django-filer.readthedocs.io/en/latest/installation.html


# Working Gmail setup with 16-dig app pw
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = "info@benaustin.de"
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")