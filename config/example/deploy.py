
DEBUG = True
ALLOWED_HOSTS = ['localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'happy',
        'USER': 'alex',
        'PASSWORD': 'admin',
        'HOST': 'localhost',
        'PORT': '',
    }
}