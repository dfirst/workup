from __future__ import unicode_literals
from workup.secret import *


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": dbname,
        "USER": dbadmin,
        "PASSWORD": dbpass,
        "HOST": dbhost,
        "PORT": dbport,
    }
}

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = allhostslist

ACCOUNTS_VERIFICATION_REQUIRED = True

EMAIL_HOST = smtp_host
EMAIL_PORT = smtp_port
EMAIL_HOST_USER = smtp_host_login
EMAIL_HOST_PASSWORD = smtp_host_pass
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = smtp_mail_sender
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

GOOGLE_ANALYTICS_ID = ganalytic

#social_auth
VKONTAKTE_APP_ID = VK_APP_ID
VKONTAKTE_APP_SECRET = VK_API_SECRET

#SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "https")

#CACHE_MIDDLEWARE_SECONDS = 60

#CACHE_MIDDLEWARE_KEY_PREFIX = "%(proj_name)s"

#CACHES = {
#    "default": {
#        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
#        "LOCATION": "127.0.0.1:11211",
#    }
#}

#SESSION_ENGINE = "django.contrib.sessions.backends.cache"
