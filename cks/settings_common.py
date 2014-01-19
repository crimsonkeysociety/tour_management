import os, os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

############################################################
##### DATABASE #############################################
############################################################

ALLOWED_HOSTS = ['*']

############################################################
##### APPS AND MIDDLEWARE ##################################
############################################################

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'widget_tweaks',
    'dbbackup',
    'social.apps.django_app.default',
    'debug_toolbar',
    'storages',
    'app',
    'public',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
)


############################################################
##### INTERNATIONALIZATION #################################
############################################################

LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = 'America/New_York'


############################################################
##### PROJECT-SPECIFIC #####################################
############################################################

# in form (month, date)
FALL_SEMESTER_START = (9, 1)
FALL_SEMESTER_END = (12, 31)

SPRING_SEMESTER_START = (1, 1)
SPRING_SEMESTER_END = (6, 1)

SEMESTER_START = {}
SEMESTER_END = {}

SEMESTER_START['fall'] = FALL_SEMESTER_START
SEMESTER_END['fall'] = FALL_SEMESTER_END
SEMESTER_START['spring'] = SPRING_SEMESTER_START
SEMESTER_END['spring'] = SPRING_SEMESTER_END

# options are 'less' or 'css'
STYLE_PROTOCOL = 'css'

############################################################
##### TEMPLATES ############################################
############################################################

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/'),
)

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
    'app.context_processors.style_protocol',
    'django.contrib.messages.context_processors.messages',
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
)

############################################################
##### AUTHENTICATION #######################################
############################################################

AUTHENTICATION_BACKENDS = (
  'social.backends.open_id.OpenIdAuth',
  'social.backends.google.GoogleOpenId',
  'social.backends.username.UsernameAuth',
  'django.contrib.auth.backends.ModelBackend',
)


LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
URL_PATH = ''
SOCIAL_AUTH_STRATEGY = 'social.strategies.django_strategy.DjangoStrategy'
SOCIAL_AUTH_STORAGE = 'social.apps.django_app.default.models.DjangoStorage'


SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details'
)


############################################################
##### EMAIL ################################################
############################################################

EMAIL_USE_TLS = True
FROM_EMAIL = os.environ.get('FROM_EMAIL')
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = os.environ.get('FROM_EMAIL')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

ADMINS = (
    ('Andrew Raftery', 'andrewraftery@gmail.com'),
    )


############################################################
##### DB BACKUPS ###########################################
############################################################

DBBACKUP_STORAGE = 'dbbackup.storage.dropbox_storage'
DBBACKUP_TOKENS_FILEPATH = '/app/oauth_tokens/oauth_tokens.txt'
DBBACKUP_DROPBOX_APP_KEY = os.environ.get('DBBACKUP_DROPBOX_APP_KEY')
DBBACKUP_DROPBOX_APP_SECRET = os.environ.get('DBBACKUP_DROPBOX_APP_SECRET')


############################################################
##### OTHER ################################################
############################################################

ROOT_URLCONF = 'cks.urls'
WSGI_APPLICATION = 'cks.wsgi.application'
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
SECRET_KEY = os.environ.get('SECRET_KEY')

DATABASES = {}