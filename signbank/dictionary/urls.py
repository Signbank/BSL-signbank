from django.conf.urls import *
from django.contrib.auth.decorators import login_required, permission_required

from signbank.dictionary.models import *
from signbank.dictionary.forms import *
from signbank.dictionary.views import feature_search

from signbank.dictionary.adminviews import GlossListView, GlossDetailView


urlpatterns = patterns('',

    # index page is just the search page
    url(r'^$', 'signbank.dictionary.views.search'),

    # we use the same view for a definition and for the feedback form on that
    # definition, the first component of the path is word or feedback in each case
    url(r'^words/(?P<keyword>.+)-(?P<n>\d+).html$',
            'signbank.dictionary.views.word', name='word_view'),

    url(r'^tag/(?P<tag>[^/]*)/?$', 'signbank.dictionary.tagviews.taglist'),

    # and and alternate view for direct display of a gloss
    url(r'gloss/(?P<idgloss>.+).html$', 'signbank.dictionary.views.gloss', name='public_gloss'),

    # Regional views for words and glosses
    url(r'^regional/(?P<keyword>.+)-(?P<n>\d+).html$',
            'signbank.dictionary.views.regional', name='regional_view'),

    url(r'^search/$', 'signbank.dictionary.views.search', name="search"),
    url(r'^featuresearch/$', 'signbank.dictionary.views.feature_search', name='feature_search'),
    url(r'^update/gloss/(?P<glossid>\d+)$', 'signbank.dictionary.update.update_gloss', name='update_gloss'),
    url(r'^update/tag/(?P<glossid>\d+)$', 'signbank.dictionary.update.add_tag', name='add_tag'),
    url(r'^update/definition/(?P<glossid>\d+)$', 'signbank.dictionary.update.add_definition', name='add_definition'),
    url(r'^update/relation/$', 'signbank.dictionary.update.add_relation', name='add_relation'),
    url(r'^update/region/(?P<glossid>\d+)$', 'signbank.dictionary.update.add_region', name='add_region'),
    url(r'^update/gloss/', 'signbank.dictionary.update.add_gloss', name='add_gloss'),

    url(r'^update_ecv/', GlossListView.as_view(only_export_ecv=True)),

    url(r'^ajax/keyword/(?P<prefix>.*)$', 'signbank.dictionary.views.keyword_value_list'),
    url(r'^ajax/tags/$', 'signbank.dictionary.tagviews.taglist_json'),
    url(r'^ajax/gloss/(?P<prefix>.*)$', 'signbank.dictionary.adminviews.gloss_ajax_complete', name='gloss_complete'),

    url(r'^missingvideo.html$', 'signbank.dictionary.views.missing_video_view'),
    
    url(r'package/$', 'signbank.dictionary.views.package'),
    url(r'info/$', 'signbank.dictionary.views.info'),

    # Admin views
    url(r'^list/$', permission_required('dictionary.search_gloss')(GlossListView.as_view()), name='admin_gloss_list'),
    url(r'^gloss/(?P<pk>\d+)', permission_required('dictionary.search_gloss')(GlossDetailView.as_view()), name='admin_gloss_view'),

)
