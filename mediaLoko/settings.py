from decouple import config

DATABASES = {
    'default': config('DATABASE_URL', cast=db_url),
}
