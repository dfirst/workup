try:
    from .secret import VK_API_SECRET, VK_APP_ID


    # VK local social_auth
    VKONTAKTE_APP_ID = VK_APP_ID
    VKONTAKTE_APP_SECRET = VK_API_SECRET
except ImportError:
    pass


DEBUG = True

# Make these unique, and don't share it with anybody.
SECRET_KEY = "e4c626e2-3fc9-443b-9c50-e6bf6db5932114071465-ac32-4775-9699-3ffebd9097f10f95db63-4b06-428b-8ef9-660fa2e1a3cf"
NEVERCACHE_KEY = "693d8a4d-71c5-464b-9958-f6375f5b5897eb49fc36-02a7-4ab8-906d-7d74a17be2df34afce09-2e04-44e6-a76e-7d7f1d58c53c"

DATABASES = {
    "default": {
        # Ends with "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
        "ENGINE": "django.db.backends.sqlite3",
        # DB name or path to database file if using sqlite3.
        "NAME": "dev.db",
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
