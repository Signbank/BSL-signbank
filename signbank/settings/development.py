from signbank.settings.base import *

#URL = "http://192.168.1.215:8000"
URL = "http://127.0.0.1:8000"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bsl_signbank',
        'USER': 'bsl',
        'PASSWORD': 'pigeon59',
        'HOST': 'localhost',
        'PORT': '',
    }
}


TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'bootstrap_templates'),
)

# show emails on the console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

PRIMARY_CSS = "bootstrap_css/bsl.css"
#PRIMARY_CSS = "bootstrap_css/auslan.css"


# defines the aspect ratio for videos
#VIDEO_ASPECT_RATIO = 360.0/640.0


# what do we call this signbank?
LANGUAGE_NAME = "BSL"
COUNTRY_NAME = "the UK"

# show/don't show sign navigation
SIGN_NAVIGATION = False

# show the number signs page or an under construction page?
#SHOW_NUMBERSIGNS = False

# do we show the 'advanced search' form and implement 'safe' search?
#ADVANCED_SEARCH = False

# which definition fields do we show and in what order?
#DEFINITION_FIELDS = []


#ADMIN_RESULT_FIELDS = ['idgloss', 'annotation_idgloss']


GLOSS_VIDEO_DIRECTORY = 'bsl-video'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
DO_LOGGING = True
LOG_FILENAME = "debug.log"


import mimetypes
mimetypes.add_type("video/mp4", ".mov", True)

MEDIA_ROOT = os.path.join(PROJECT_DIR, "media")
WRITABLE_FOLDER = os.path.join(PROJECT_DIR, "files") + "/"
WRITABLE_URL = "/files/"

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

# a list of tags we're allowed to use
XALLOWED_TAGS = [ '',
                 'workflow:unlemmatised',
                 'workflow:lemmatised',
                 'workflow:redo video',
                 'workflow:problematic',
                 'b92:directional',
                 'b92:regional',
                 'b92:variant',
                 'corpus:attested',
                 'lexis:doubtlex',
                 'phonology:alternating',
                 'phonology:dominant hand only',
                 'phonology:double handed',
                 'phonology:forearm rotation',
                 'phonology:handshape change',
                 'phonology:onehand',
                 'phonology:parallel',
                 'phonology:symmetrical',
                 'phonology:two handed',
                ]
