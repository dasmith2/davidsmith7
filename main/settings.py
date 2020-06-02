"""
Don't modify this file on specific sites. Use this_site_settings.py for that.
This file should stay the same between all the sites.
"""
import os
import re
import sys
import warnings

import django_heroku


""" What environment are you in? Just check your settings! """
DEBUG = os.path.exists('main/local_settings.py')
LOCAL = DEBUG
STAGE = os.environ.get('STAGE', default='False') == 'True'
PROD = os.environ.get('PROD', default='False') == 'True'
TEST = 'test' in sys.argv
RUNSERVER = 'runserver' in sys.argv
GUNICORN = 'gunicorn' in sys.argv
WEB = RUNSERVER or GUNICORN
MANAGE_COMMAND_FINDER = re.compile(r'[^\w]*manage.py')
MANAGE_COMMAND = any([MANAGE_COMMAND_FINDER.match(arg) for arg in sys.argv])
SHELL = MANAGE_COMMAND and 'shell' in sys.argv
IN_WORKER = 'worker.py' in sys.argv
# This is a little ugly. There are two cases where you'd be in a background
# thread. One is you're a task that was picked up by worker.py, the background
# thread worker as defined in Procfile. The other is you're a custom management
# command. Hopefully, runserver is the only non-custom mangement command that
# cares about this setting. This is less of an issue now that we use clock.py
# but we still have a few management commands available.
BACKGROUND = IN_WORKER or (MANAGE_COMMAND and not RUNSERVER)
IS_CLOCK = 'clock.py' in sys.argv
# This gets set in app.json
IN_HEROKU_CI = os.environ.get('IN_HEROKU_CI', default=False)


""" Email stuff. """
# All code ought to make sense in production, the shell, tests, web tests, and
# web demos. log_error is a bit of a special case. By default in tests and the
# shell it shouldn't send emails. But one time, sending emails was precisely
# the thing that was broken and I couldn't experiment in the shell. Now you can
# do this in the shell:
#
# from django.conf import settings; settings.ALWAYS_ALLOW_SEND_MAIL = True
# log_error('hello', 'world') # Will actually email
ALWAYS_ALLOW_SEND_MAIL = False

# Django will automatically mail a full traceback of any error to each person
# listed in the ADMINS
ADMINS = []
EMAIL_ERRORS_TO = os.environ.get(
    'EMAIL_STACK_TRACES_TO', default='dave@davespace.tech')
if EMAIL_ERRORS_TO:
  ADMINS.append(
      ('Heroku errors', EMAIL_ERRORS_TO))

# Otherwise, when Django sends emails to the admins due to 500 errors, they're
# from root@localhost and no self respecting smtp provider lets that through.
# You'll probably need to override this in this_site_settings
SERVER_EMAIL = 'server@davespace.tech'

# There are two huge different use cases for email. One is emailing staff
# members about internal things, such as emailing software developers about
# server errors. The other use case is emailing users, which must be handled
# with more sensitivity. For instance, users can unsubscribe. Staff emails and
# user emails should come from different domains from each other AND different
# domains from the site because it's oh-so-easy for a domain to get marked
# spam. So I'm not a huge fan of these global email settings, implying as they
# do that a single email setup per site is sufficient. But I use them because
# it means I don't have to write my own error handling middleware. This way,
# Django will automatically email whoever is in the ADMINS list whenever
# there's a hard error. The free tier of Mailgun is good enough for this
# purpose.
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY', default='')
MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN', default='')
MAILGUN_PUBLIC_KEY = os.environ.get('MAILGUN_PUBLIC_KEY', default='')
MAILGUN_SMTP_LOGIN = os.environ.get('MAILGUN_SMTP_LOGIN', default='')
MAILGUN_SMTP_PASSWORD = os.environ.get('MAILGUN_SMTP_PASSWORD', default='')
MAILGUN_SMTP_PORT = os.environ.get('MAILGUN_SMTP_PORT', default='')
MAILGUN_SMTP_SERVER = os.environ.get('MAILGUN_SMTP_SERVER', default='')

EMAIL_HOST = MAILGUN_SMTP_SERVER
EMAIL_PORT = MAILGUN_SMTP_PORT
EMAIL_HOST_USER = MAILGUN_SMTP_LOGIN
EMAIL_HOST_PASSWORD = MAILGUN_SMTP_PASSWORD


""" Network stuff. """
# So, we want to avoid any environment BUT prod from messing with external
# APIS. The last thing we want is, say, tests creating eroneous cleanings by
# accident. But just in case you actually do need to use APIs and such locally.
ALLOW_NETWORK_OVERRIDE = False

NETWORK_READS_OK = SHELL or BACKGROUND
NETWORK_WRITES_OK = PROD and NETWORK_READS_OK

# Notifications for requests that take too long
MAX_ALLOWED_REQUEST_TIME = 0.5  # seconds


""" URL stuff. """
SECURE_SSL_REDIRECT = not IN_HEROKU_CI and not DEBUG

APPEND_SLASH = False

THIS_SERVERS_BASE_URL_SET = bool(os.environ.get(
    'THIS_SERVERS_BASE_URL', default=False))
THIS_SERVERS_BASE_URL = os.environ.get(
    'THIS_SERVERS_BASE_URL',
    default=(
        'Please set the THIS_SERVERS_BASE_URL environment variable with '
        'no trailing /'))

ROOT_URLCONF = 'main.urls'
# "Allow the debug() context processor to add some variables to the template
# context"
INTERNAL_IPS = ['127.0.0.1']

ALLOWED_HOSTS = []
# If ALLOWED_HOSTS is empty and DEBUG = True it uses something like
# ['127.0.0.1', 'localhost']
if STAGE or PROD:
  ALLOWED_HOSTS = [THIS_SERVERS_BASE_URL]


""" File stuff. """
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Utterly vague names here, huh. STATICFILES_DIRS is where to collect FROM, and
# STATIC_ROOT is where to collect TO.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static_files')

STATIC_URL = '/static/'


""" Secret key. """
DEFAULT_SECRET_KEY = 'DEFAULT_SECRET_KEY'
SECRET_KEY = os.environ.get('SECRET_KEY', DEFAULT_SECRET_KEY)
if (PROD or STAGE) and SECRET_KEY == DEFAULT_SECRET_KEY:
  raise Exception(
      'Set the SECRET_KEY environment variable to a long random string')


""" API stuff """
API_KEY_TYPES = ['djaveAPI.models.user_api_key.UserAPIKey']


""" Telling Django about packages. Don't put site specific packages here. Put
them in THIS_SITE_INSTALLED_APPS in main/this_site_installed_apps.py """
from main.this_site_installed_apps import THIS_SITE_INSTALLED_APPS

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djaveAPI',
    'djavError',
    'djaveLogin',
    'djaveReport',
    'djaveS3',
    'djaveThread'] + THIS_SITE_INSTALLED_APPS

# Whichever of these test classes reference django.contrib.auth.User need
# explicit migrations to work. I did that by uncommenting "if TEST:" here,
# briefly creating for example djaveAPI/tests/migrations, configuring
# djaveAPI/tests/apps.py, then ./manage.py makemigrations
if TEST or IN_HEROKU_CI:
  INSTALLED_APPS.append('djaveAPI.tests.apps.DjaveAPITestsConfig')

if DEBUG:
  # I try to keep things out of requirements.txt that aren't necessary in the
  # server enviroment because Heroku likes to choke unexpectedly and with
  # unhelpful messages depending on requirements. Locally you'll want to do
  # something like pip install django-debug-toolbar
  INSTALLED_APPS.append('debug_toolbar')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
  MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')


""" Template stuff. """
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['main/templates', 'djaveNav/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

TEMPLATE_STRING_IF_INVALID = 'Invalid template variable: %s'

if DEBUG:
  # This gives us stack traces for non-timezone-aware warnings.
  warnings.filterwarnings(
      'error', r"DateTimeField .* received a naive datetime",
      RuntimeWarning, r'django\.db\.models\.fields')


""" Password validation. """
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',  # noqa: E501
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',  # noqa: E501
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',  # noqa: E501
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',  # noqa: E501
    },
]

AUTHENTICATION_BACKENDS = [
    'djaveLogin.authentication_backend.AuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend']


""" Internationalization. """
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEFAULT_CURRENCY = 'USD'


""" ??? """
WSGI_APPLICATION = 'main.wsgi.application'


""" Environment variable overrides, local and on Heroku. """
# I stopped using django-environ mainly because it was confusing. But also it
# wasn't reflecting os.environ in Heroku's CI environment which is, like, you
# had one job.

# Keys for APIs go in this_site_settings because who knows which APIs each site
# is going to hook up with.
from main.this_site_settings import *  # noqa: F401,F403

try:
  # This is where you put your laptop database settings, for instance.
  from main.local_settings import *  # noqa: F401,F403
except ModuleNotFoundError:
  pass

django_heroku.settings(locals())
