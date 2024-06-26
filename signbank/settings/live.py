# Configuration for live BSL signbank site at http://bslsignbank.ucl.ac.uk
# This configuration should not be made public or stored in a public repository

from signbank.settings.base import *
import os

DEBUG = False
TEMPLATE_DEBUG = DEBUG

URL = "https://bslsignbank.ucl.ac.uk"

ADMINS = (
     ('Marc Sutton', 'marc@codev.co.uk'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bsl_signbank',
        'USER': 'bsl',
        'PASSWORD': 'pigeon599',
        'HOST': 'postgresdb',
#        'PORT': '',
    }
}

CHECKOUT_DIR = '/home/app/data/apps/signbank/checkout/BSL-signbank'
UPLOADS_DIR = '/home/app/data/uploads/signbank'

TEMPLATE_DIRS = (
    CHECKOUT_DIR + '/bootstrap_templates',
)

DEFINITION_ROLE_CHOICES = (
    ('note', 'Note'),
    ('privatenote', 'Private Note'),
    ('B92 sn', 'Sign Number in Brien 92'),
)

# Email configuration, used to use smtp-server.ucl.ac.uk when it was internal, now Amazon SES
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'AKIAX2YYSRFZR4QTNRKD'
EMAIL_HOST_PASSWORD = 'BGIw+O0+9rxwAPhVYZKqUAjQjXim39UWzmqEOEQAsXPK'

ADMIN_EMAIL = "bslsignbank@ucl.ac.uk"
DEFAULT_FROM_EMAIL = "bslsignbank@ucl.ac.uk"
SERVER_EMAIL = "bslsignbank@ucl.ac.uk"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
# Static files are served by the webserver as of 2022, not django
STATIC_ROOT = UPLOADS_DIR + '/static/'
STATIC_URL = '/static/'

MEDIA_ROOT = UPLOADS_DIR + '/media/'
MEDIA_URL = "/media/"
MEDIA_MOBILE_URL = MEDIA_URL

WRITABLE_FOLDER = UPLOADS_DIR + '/writable/'
WRITABLE_URL = "/files/"
SIGNBANK_PACKAGES_FOLDER = WRITABLE_FOLDER+'packages/'

UPLOAD_ROOT = WRITABLE_FOLDER
UPLOAD_URL = WRITABLE_URL

ECV_FILENAME = 'bsl.ecv'
ECV_FILE = os.path.join(WRITABLE_FOLDER, ECV_FILENAME)
ECV_URL = URL + WRITABLE_URL + ECV_FILENAME
ECV_SETTINGS = {
    'CV_ID': 'BSL-lexicon',
    'include_phonology_and_frequencies': True,
    'languages': [
        {
            'id': 'eng',
            'description': 'The glosses CV for the BSL',
            'annotation_idgloss_fieldname': 'annotation_idgloss',
            'attributes': {
                'LANG_DEF': 'http://cdb.iso.org/lg/CDB-00138502-001',
                'LANG_ID': 'eng',
                'LANG_LABEL': 'English (eng)'
            }
        },
    ]
}

# should be customised on the production server and not kept in VC
SECRET_KEY = '^g=q21r_ourpwor029303*2gvplf8218&^(_)jp;t3k2r3c$*u&amp;2la5!%s'

ALLOWED_HOSTS = ['bslsignbank.ucl.ac.uk', 'bslsignbank.ucl.ac.codev', 'bslsignbank.codev.uk', 'bslsignbank.codev.codev']


PRIMARY_CSS = "bootstrap_css/bsl.css"
MOBILE_CSS = "bootstrap_css/mobile-extra-bsl.css"

# show/don't show sign navigation
SIGN_NAVIGATION = False

# defines the aspect ratio for videos
VIDEO_ASPECT_RATIO = 360.0/640.0


# what do we call this signbank?
LANGUAGE_NAME = "BSL"
COUNTRY_NAME = "the UK"
SITE_TITLE = "BSL SignBank"

GOOGLE_ANALYTICS_TRACKING_CODE = "UA-62204298-1"

SOCIAL_NETWORK_SHARE_LINKS = True
SOCIAL_NETWORK_FACEBOOK_PAGE = "https://www.facebook.com/pages/DCAL-Deafness-Cognition-and-Language-Research-Centre/136511306447860"
SOCIAL_NETWORK_TWITTER_PAGE = "https://twitter.com/DCAL_UCL"

ADVANCED_SEARCH = False

# show the number signs page or an under construction page?
SHOW_NUMBERSIGNS = False


ADMIN_RESULT_FIELDS = ['idgloss', 'annotation_idgloss']


# within MEDIA_ROOT we store newly uploaded videos in this directory
GLOSS_VIDEO_DIRECTORY = "bsl-video"

# location of ffmpeg, used to convert uploaded videos
FFMPEG_PROGRAM = "/usr/bin/ffmpeg"
FFMPEG_TIMEOUT = 60
#FFMPEG_OPTIONS = ["-vcodec", "libx264", "-an", "-vpre", "hq", "-s", "320x240", "-r", "30000/1001", "-b", "200k", "-bt", "240k"]
FFMPEG_OPTIONS = ["-vcodec", "libx264", "-an", "-b",  "1500k"]



# a list of tags we're allowed to use
ALLOWED_TAGS = [ '',
                 'workflow:unlemmatised',
                 'workflow:lemmatised',
                 'workflow:redo video',
                 'workflow:problematic',
                 'b92:directional',
                 'b92:regional',
                 'b92:variant',
                 'b92:present',
                 'corpus:attested',
                 'lexis:crude',
                 'lexis:doubtlex',
                 'lexis:fingerspell',
                 'morphology:variant',
                 'phonology:alternating',
                 'phonology:dominant hand only',
                 'phonology:double handed',
                 'phonology:forearm rotation',
                 'phonology:handshape change',
                 'phonology:onehand',
                 'phonology:parallel',
                 'phonology:symmetrical',
                 'phonology:two handed',
                 'phonology:variant',
                 'corpus:directional',
                 'model:left',
                ]

# Development settings
if os.environ['CODEV_ENV'] == 'development' or os.environ['PASSENGER_APP_ENV'] == 'development':
  DEBUG = True

  ADMIN_EMAIL = "info@codev.uk"
  DEFAULT_FROM_EMAIL = "info@codev.uk"
  SERVER_EMAIL = "info@codev.uk"
