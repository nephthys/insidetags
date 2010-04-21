# Django settings for insidetags project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('', ''),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr-fr'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/site_media/'

STATIC_ROOT = ''



# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'sn=ub*dww=5yl^(8-iy6=3cfq7pi!4g1v_!qd=cb5k+1qbqldq'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'openid_consumer.middleware.OpenIDMiddleware',
    'insidetags.apps.middleware.threadlocals.ThreadLocals',
    'insidetags.apps.middleware.nextpage.SaveNextPage',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'insidetags.apps.posts.context_processors.context_base',
    'socialauth.context_processors.facebook_api_key',
    
)

ROOT_URLCONF = 'insidetags.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    ''
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.comments',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'insidetags.apps.posts',
    'insidetags.apps.users',
    'insidetags.apps.extflatpages',
    'threadedcomments',
    'socialauth',
    'openid_consumer',
    'commentor',
    'tagging',
)

COMMENTS_APP = 'threadedcomments'
THREADEDCOMMENTS_SELECT_RELATED = ['user']
AUTH_PROFILE_MODULE = 'users.UserProfile'

OPENID_REDIRECT_NEXT = '/accounts/openid/done/'
 
OPENID_SREG = {"requred": "nickname, email",
               "optional":"postcode, country",
               "policy_url": ""}
 
OPENID_AX = [{"type_uri": "email",
              "count": 1,
              "required": True,
              "alias": "email"},
             {"type_uri": "fullname",
              "count":1 ,
              "required": False,
              "alias": "fullname"}]
 
TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''
 
FACEBOOK_API_KEY = ''
FACEBOOK_SECRET_KEY = ''
 
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'socialauth.auth_backends.OpenIdBackend',
    'socialauth.auth_backends.TwitterBackend',
    'socialauth.auth_backends.FacebookBackend',
)

LOGIN_REDIRECT_URL = '/accounts/done/'
LOGIN_REDIRECT_BOARD = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'
