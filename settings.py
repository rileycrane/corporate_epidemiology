# Django settings for corporate_epidemiology project.
import os, sys
ROOT_PATH = os.path.dirname(__file__) 
sys.path.append(os.path.join(ROOT_PATH))

PATH_TO_CORP_EPI = ROOT_PATH
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(ROOT_PATH, 'epi.db'),                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
	'version': 1,

	'disable_existing_loggers': True,

	'formatters': {
		'verbose': {
			'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
		},
		'simple': {
			'format': '%(levelname)s %(message)s'
		},
		'intermediate': {
			'format': '%(levelname)s | %(asctime)s | %(module)s | %(funcName)s | %(lineno)d :: %(message)s',
			'datefmt':'%a, %d %b %H:%M:%S',
		},

	},

	'handlers': {
		'null': {
			'level':'DEBUG',
			'class':'django.utils.log.NullHandler',
		},
		'console':{
			'level':'DEBUG',
			'class':'logging.StreamHandler',
			'formatter': 'simple'
		},
		'mail_admins': {
			'level': 'ERROR',
			'class': 'django.utils.log.AdminEmailHandler',
		},
		'rotating_file_handler': {
			'level': 'DEBUG',
			'class': 'logging.handlers.RotatingFileHandler',
			'formatter': 'intermediate',
			'filename': os.path.join(PATH_TO_CORP_EPI,'log','simulation.log'),
			'maxBytes': 10*1024*1024,
			'backupCount': 0,
		},
	},
	'loggers': {
		'django': {
			'handlers':['null'],
			'propagate': True,
			'level':'INFO',
		},
		'django.request': {
			'handlers': ['mail_admins'],
			'level': 'ERROR',
			'propagate': False,
		},
		'corp_epi': {
			'handlers': ['rotating_file_handler'],
			'propagate': True,
			'level': 'INFO',
		}
	}

}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(ROOT_PATH, 'media')
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '127.0.0.1:8000/media'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'nvw#b-p@lv$furq_99y7=_8zp1gb-tgf7bl@@(%na=v243xl(1'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'corporate_epidemiology.urls'

TEMPLATE_DIRS = (
	os.path.join(ROOT_PATH, 'templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
	'django.core.context_processors.request',
	'django.contrib.auth.context_processors.auth',
	'django.contrib.messages.context_processors.messages',
	'django.core.context_processors.media',    
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'simulations',
    'django.contrib.admindocs',
    'django_extensions',
)
