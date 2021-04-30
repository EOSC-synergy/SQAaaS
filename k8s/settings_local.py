# settings_local.py is for all instance specific settings
import random
from settings import *
from mainsite import TOP_DIR
DEBUG = True
DEBUG_ERRORS = DEBUG
DEBUG_STATIC = DEBUG
DEBUG_MEDIA = DEBUG
TIME_ZONE = 'Europe/Madrid'
LANGUAGE_CODE = 'en-us'
STATIC_URL =  "/static/"
##
#
# Database Configuration
#
##
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'badgrdb',                      # Or path to database file if using sqlite3.
        'USER': 'badgruser',                      # Not used with sqlite3.
        'PASSWORD': 'badgr-mysql-pass',                  # Not used with sqlite3.
        'HOST': 'mysql',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
        'OPTIONS': {
#            "SET character_set_connection=utf8mb3, collation_connection=utf8_unicode_ci",  # Uncomment when using MySQL to ensure consistency across servers
        },
    }
}
###
#
# CACHE
#
###
# Example 1: LocMemCache (volatile, but simplest)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': '',
        'TIMEOUT': 300,
        'KEY_PREFIX': '',
        'VERSION': 1,
    }
}
###
#
# Email Configuration
#
###
DEFAULT_FROM_EMAIL = ''  # e.g. "noreply@example.com"
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
###
#
# Celery Asynchronous Task Processing (Optional)
#
###
# BROKER_URL = 'amqp://localhost:5672/'
CELERY_RESULT_BACKEND = None
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULTS_SERIALIZER = 'json'
# CELERY_ACCEPT_CONTENT = ['json']
# Run celery tasks in same thread as webserver (True means that asynchronous processing is OFF)
CELERY_ALWAYS_EAGER = True
###
#
# Application Options Configuration
#
###
HTTP_ORIGIN = 'http://badgrserver:8000'
# Optionally restrict issuer creation to accounts that have the 'issuer.add_issuer' permission
BADGR_APPROVED_ISSUERS_ONLY = False
# Automatically send an email the first time that recipient identifier (email type) has been used on the system.
GDPR_COMPLIANCE_NOTIFY_ON_FIRST_AWARD = True
LOGS_DIR = TOP_DIR + '/logs'
ALLOWED_HOSTS = ['*']
SECRET_KEY = 'QKQ9NKGJLXE8UVS3TXIB0DE7Q9W41J578C5FCRJL'  # ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(40))
UNSUBSCRIBE_KEY = '8GGGDKOT4H4O7QU4GPGZ7ERY9GPE2FKALAO81WYP'  # ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(40))
UNSUBSCRIBE_SECRET_KEY = '8GGGDKOT4H4O7QU4GPGZ7ERY9GPE2FKALAO81WYP'
###
#
# Logging
#
###
LOGS_DIR = os.path.join(TOP_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': [],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        # badgr events log to disk by default
        'badgr_events': {
            'level': 'INFO',
            'formatter': 'json',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'badgr_events.log')
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        # Badgr.Events emits all badge related activity
        'Badgr.Events': {
            'handlers': ['badgr_events'],
            'level': 'INFO',
            'propagate': False,
        }
    },
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s %(module)s %(message)s'
        },
        'json': {
            '()': 'mainsite.formatters.JsonFormatter',
            'format': '%(asctime)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S%z',
        }
    },
}