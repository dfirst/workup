try:
    from .secret import VK_API_SECRET, VK_APP_ID
    # VK local social_auth
    VKONTAKTE_APP_ID = VK_APP_ID
    VKONTAKTE_APP_SECRET = VK_API_SECRET
except ImportError:
    pass


DEBUG = True

# Make these unique, and don't share it with anybody.
SECRET_KEY = "local-settings"
NEVERCACHE_KEY = "local-settings"

DATABASES = {
    "default": {
        # Ends with "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
        "ENGINE": "django.db.backends.sqlite3",
        # DB name or path to database file if using sqlite3.
        "NAME": "../dev.db",
        # Not used with sqlite3.
        "USER": "",
        # Not used with sqlite3.
        "PASSWORD": "",
        # Set to empty string for localhost. Not used with sqlite3.
        "HOST": "",
        # Set to empty string for default. Not used with sqlite3.
        "PORT": "",
    }
}

# Social_auth
SOCIAL_AUTH_RAISE_EXCEPTIONS = DEBUG
