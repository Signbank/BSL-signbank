from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, RequestContext, loader
from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from tagging.models import Tag, TaggedItem
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.safestring import mark_safe

from django.utils.encoding import smart_unicode

import os
import re
import json
import time
from wsgiref.util import FileWrapper

from signbank.dictionary.models import *
from signbank.dictionary.forms import *
from signbank.feedback.models import *
from signbank.pages.models import *
import signbank.tools

from signbank.video.forms import VideoUploadForGlossForm
from signbank.log import debug

def login_required_config(f):
    """like @login_required if the ALWAYS_REQUIRE_LOGIN setting is True"""

    if settings.ALWAYS_REQUIRE_LOGIN:
        return login_required(f)
    else:
        return f



@login_required_config
def index(request):
    """Default view showing a browse/search entry
    point to the dictionary"""


    return render_to_response("dictionary/search_result.html",
                              {'form': UserSignSearchForm(),
                               'language': settings.LANGUAGE_NAME,
                               'query': '',
                               },
                               context_instance=RequestContext(request))



def map_image_for_regions(regions):
    """Get the right map images for this region set
    """

    # Add a map for every unique language and dialect we have
    # regional information on
    # This may look odd if there is more than one language
    images = []
    for region in regions.all():
        language_name = region.dialect.language.name.replace(" ", "")
        dialect_name = region.dialect.name.replace(" ", "")
        dialect_extension = ""
        if region.traditional:
            dialect_extension = "-traditional"

        language_filename = "images/maps/" + language_name + ".png"
        dialect_filename = "images/maps/" + language_name + "/" + dialect_name + dialect_extension + ".png"

        if language_filename not in images:
            images.append(language_filename)
        if dialect_filename not in images:
            images.append(dialect_filename)

    return images


@login_required_config
def word_and_regional_view(request, keyword, n, viewname):
    """
    Helper view that displays the word or the regional view depending on what
    viewname is set to
    """

    n = int(n)

    if request.GET.has_key('feedbackmessage'):
        feedbackmessage = request.GET['feedbackmessage']
    else:
        feedbackmessage = False

    word = get_object_or_404(Keyword, text=keyword)

    # returns (matching translation, number of matches)
    (trans, total) =  word.match_request(request, n, )

    # and all the keywords associated with this sign
    allkwds = trans.gloss.translation_set.all()

    videourl = trans.gloss.get_video_url()
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, videourl)):
        videourl = None

    trans.homophones = trans.gloss.relation_sources.filter(role='homophone')

    # work out the number of this gloss and the total number
    gloss = trans.gloss
    if gloss.sn != None:
        if request.user.has_perm('dictionary.search_gloss'):
            glosscount = Gloss.objects.count()
            glossposn = Gloss.objects.filter(sn__lt=gloss.sn).count()+1
        else:
            glosscount = Gloss.objects.filter(inWeb__exact=True).count()
            glossposn = Gloss.objects.filter(inWeb__exact=True, sn__lt=gloss.sn).count()+1
    else:
        glosscount = 0
        glossposn = 0

    # navigation gives us the next and previous signs
    nav = gloss.navigation(request.user.has_perm('dictionary.search_gloss'))

    # the gloss update form for staff

    if request.user.has_perm('dictionary.search_gloss'):
        update_form = GlossModelForm(instance=trans.gloss)
        video_form = VideoUploadForGlossForm(initial={'gloss_id': trans.gloss.pk,
                                                      'redirect': request.path})
    else:
        update_form = None
        video_form = None

    # Regional list (sorted by dialect name) and regional template contents if this gloss has one
    regions = sorted(gloss.region_set.all(), key=lambda n: n.dialect.name)
    try:
        page = Page.objects.get(url__exact=gloss.regional_template)
        regional_template_content = mark_safe(page.content)
    except:
        regional_template_content = None

    # If we asked for a regional view but there is no regional information available redirect to non regional view
    if viewname == "regional" and len(regions) == 0:
        return HttpResponseRedirect('/dictionary/words/'+keyword+'-'+str(n)+'.html' )

    return render_to_response("dictionary/word.html",
                              {'translation': trans,
                               'viewname': viewname,
                               'definitions': trans.gloss.definitions(),
                               'gloss': trans.gloss,
                               'allkwds': allkwds,
                               'n': n,
                               'total': total,
                               'matches': range(1, total+1),
                               'navigation': nav,
                               'dialect_image': map_image_for_regions(gloss.region_set),
                               'regions': regions,
                               'regional_template_content': regional_template_content,
                               # lastmatch is a construction of the url for this word
                               # view that we use to pass to gloss pages
                               # could do with being a fn call to generate this name here and elsewhere
                               'lastmatch': str(trans.translation)+"-"+str(n),
                               'videofile': videourl,
                               'update_form': update_form,
                               'videoform': video_form,
                               'gloss': gloss,
                               'glosscount': glosscount,
                               'glossposn': glossposn,
                               'feedback' : True,
                               'feedbackmessage': feedbackmessage,
                               'tagform': TagUpdateForm(),
                               'SIGN_NAVIGATION' : settings.SIGN_NAVIGATION,
                               'DEFINITION_FIELDS' : settings.DEFINITION_FIELDS,
                               },
                               context_instance=RequestContext(request))

@login_required_config
def word(request, keyword, n):
    """View of a single keyword that may have more than one sign"""

    return word_and_regional_view(request, keyword, n, "words")

@login_required_config
def regional(request, keyword, n):
    """View of a single keyword that may have more than one sign alongside regional information"""

    return word_and_regional_view(request, keyword, n, "regional")

def quiz(request):
    """Quiz on meanings and regions, added for the BSL anniversary"""

    # Values are:
    # 1. Gloss ID
    # 2. Incorrect answers
    # 3. True or False - if True and there are multiple regions then a question about
    #      the commonest region will be added, otherwise the region question will be skipped
    quiz_values = [
      ['BRISTOL02', "['Cardiff', 'purple', 'France']", False],
      ['FRANCE05',  "['China', 'India', 'Glasgow']", False],
      ['GREY04',    "['Belfast', 'Ireland', 'yellow']", False],
      ['AMERICA03', "['Ireland', 'purple', 'Manchester']", False],
      ['BRITAIN',   "['London', 'Bristol', 'grey']", False],
      ['PURPLE02',  "['green', 'India', 'Germany']", True],
      ['ITALY',     "['China', 'Glasgow', 'grey']", False],
      ['YELLOW04',  "['brown', 'America', 'London']", True],
    ]

    quiz = []
    for q in quiz_values:
      idgloss = q[0]
      gloss = Gloss.objects.filter(idgloss=idgloss)[0]
      wrong_answers = q[1]
      commonest_region = q[2]
      if commonest_region:
        commonest_region = gloss.region_set.order_by('-frequency').first().dialect.description

      quiz.append({
        'video_num': gloss.pk,
        'keyword': gloss.translation_set.first().translation.text,
        'link': "/dictionary/gloss/" + idgloss + ".html",
        'regions_and_frequencies': [[str(x.dialect.description),
                                      str(x.frequency),
                                      str(x.traditional).lower()]
                                      for x in gloss.region_set.all()],
        'region_list': [str(x.dialect.description) for x in gloss.region_set.all()],
        'region_images': map_image_for_regions(gloss.region_set),
        'wrong_answers': wrong_answers,
        'commonest_region': commonest_region,
      })

    return render_to_response("dictionary/quiz.html",
                              {
                                'bsl': True,
                                'debug': settings.DEBUG,
                                'quiz': quiz,
                              },
                              context_instance=RequestContext(request))

@login_required_config
def gloss(request, idgloss):
    """View of a gloss - mimics the word view, really for admin use
       when we want to preview a particular gloss"""


    if request.GET.has_key('feedbackmessage'):
        feedbackmessage = request.GET['feedbackmessage']
    else:
        feedbackmessage = False

    # we should only be able to get a single gloss, but since the URL
    # pattern could be spoofed, we might get zero or many
    # so we filter first and raise a 404 if we don't get one
    if request.user.has_perm('dictionary.search_gloss'):
        glosses = Gloss.objects.filter(idgloss=idgloss)
    else:
        glosses = Gloss.objects.filter(inWeb__exact=True, idgloss=idgloss)

    if len(glosses) != 1:
        raise Http404

    gloss = glosses[0]

    # and all the keywords associated with this sign
    allkwds = gloss.translation_set.all()
    if len(allkwds) == 0:
        trans = Translation()
    else:
        trans = allkwds[0]

    videourl = gloss.get_video_url()
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, videourl)):
        videourl = None

    if gloss.sn != None:
        if request.user.has_perm('dictionary.search_gloss'):
            glosscount = Gloss.objects.count()
            glossposn = Gloss.objects.filter(sn__lt=gloss.sn).count()+1
        else:
            glosscount = Gloss.objects.filter(inWeb__exact=True).count()
            glossposn = Gloss.objects.filter(inWeb__exact=True, sn__lt=gloss.sn).count()+1
    else:
        glosscount = 0
        glossposn = 0

    # navigation gives us the next and previous signs
    nav = gloss.navigation(request.user.has_perm('dictionary.search_gloss'))

    # the gloss update form for staff
    update_form = None

    if request.user.has_perm('dictionary.search_gloss'):
        update_form = GlossModelForm(instance=gloss)
        video_form = VideoUploadForGlossForm(initial={'gloss_id': gloss.pk,
                                                      'redirect': request.get_full_path()})
    else:
        update_form = None
        video_form = None



    # get the last match keyword if there is one passed along as a form variable
    if request.GET.has_key('lastmatch'):
        lastmatch = request.GET['lastmatch']
        if lastmatch == "None":
            lastmatch = False
    else:
        lastmatch = False

    # Regional list (sorted by dialect name) and regional template contents if this gloss has one
    regions = sorted(gloss.region_set.all(), key=lambda n: n.dialect.name)
    try:
        page = Page.objects.get(url__exact=gloss.regional_template)
        regional_template_content = mark_safe(page.content)
    except:
        regional_template_content = None

    return render_to_response("dictionary/word.html",
                              {'translation': trans,
                               'definitions': gloss.definitions(),
                               'allkwds': allkwds,
                               'dialect_image': map_image_for_regions(gloss.region_set),
                               'regions': regions,
                               'regional_template_content': regional_template_content,
                               'lastmatch': lastmatch,
                               'videofile': videourl,
                               'viewname': word,
                               'feedback': None,
                               'gloss': gloss,
                               'glosscount': glosscount,
                               'glossposn': glossposn,
                               'navigation': nav,
                               'update_form': update_form,
                               'videoform': video_form,
                               'tagform': TagUpdateForm(),
                               'feedbackmessage': feedbackmessage,
                               'SIGN_NAVIGATION' : settings.SIGN_NAVIGATION,
                               'DEFINITION_FIELDS' : settings.DEFINITION_FIELDS,
                               },
                               context_instance=RequestContext(request))

@login_required_config
def feature_search(request):
    """
    Search by hand and location features as well as, or instead of, keywords.
    """

    form = UserSignSearchForm(request.GET.copy())

    term = ''
    glosses = []
    query_valid = False

    if form.is_valid():
        # need to transcode the query to our encoding
        term = form.cleaned_data['query']
        handshape = form.cleaned_data['handshape']
        location = form.cleaned_data['location']

        if (term == '' and
          (handshape == '' or handshape == 'notset') and
          (location == '' or location == '-1')):
            query_valid = False
        else:
            query_valid = True

            try:
                term = smart_unicode(term)
            except:
                # if the encoding didn't work this is
                # a strange unicode or other string
                # and it won't match anything in the dictionary
                glosses = []

            if request.user.has_perm('dictionary.search_gloss'):
                # staff get to see all the glosses
                glosses = Gloss.objects.filter(translation__isnull=False).distinct()
            else:
                # regular users see either everything that's published
                glosses = Gloss.objects.filter(inWeb__exact=True).distinct()

            if term != '':
                glosses = glosses.filter(translation__translation__text__istartswith=term)

            if location != '' and location != "-1":
                glosses = glosses.filter(locprim__exact=location)

            if handshape != '' and handshape != "notset":
                glosses = glosses.filter(domhndsh__exact=handshape)


    paginator = Paginator(glosses, 1)
    if request.GET.has_key('page'):

        page = request.GET['page']
        try:
            result_page = paginator.page(page)
        except PageNotAnInteger:
            result_page = paginator.page(1)
        except EmptyPage:
            result_page = paginator.page(paginator.num_pages)

    else:
        result_page = paginator.page(1)


    span = 4
    page = result_page.number

    first_page = page - span
    if first_page <= 1:
      first_page = 1
      page_range_pre = []
    else:
      page_range_pre = [1]
      if first_page > 2:
        page_range_pre += ['...']

    last_page = page + span
    if last_page >= paginator.num_pages:
      last_page = paginator.num_pages
      page_range_post = []
    else:
      page_range_post = [paginator.num_pages]
      if last_page < paginator.num_pages - 1:
        page_range_post = ['...'] + page_range_post

    page_range = page_range_pre + range(first_page, last_page + 1) + page_range_post


    if len(result_page.object_list) > 0:
        gloss = result_page.object_list.first()
        keyword, index = gloss.get_keyword_and_index(request)
    else:
        gloss = None
        keyword = ''
        index = 0

    return render_to_response("dictionary/feature_search.html",
                              {'query_valid': query_valid,
                               'query': term,
                               'handshape': handshape,
                               'location': location,
                               'form': form,
                               'glosscount' : len(glosses),
                               'paginator' : paginator,
                               'page' : result_page,
                               'page_range': page_range,
                               'gloss': gloss,
                               'keyword': keyword,
                               'index': index,
                               'feature_search_active': True,
                               'language': settings.LANGUAGE_NAME,
                               },
                              context_instance=RequestContext(request))


@login_required_config
def search(request):
    """Handle keyword search form submission"""

    form = UserSignSearchForm(request.GET.copy())

    if form.is_valid() and len(form.cleaned_data['query']) > 0:
        # need to transcode the query to our encoding
        term = form.cleaned_data['query']
        category = form.cleaned_data['category']

        # safe search for authenticated users if the setting says so
        safe = (not request.user.is_authenticated()) and settings.ANON_SAFE_SEARCH

        try:
            term = smart_unicode(term)
        except:
            # if the encoding didn't work this is
            # a strange unicode or other string
            # and it won't match anything in the dictionary
            words = []

        if request.user.has_perm('dictionary.search_gloss'):
            # staff get to see all the words that have at least one translation
            words = Keyword.objects.filter(text__istartswith=term, translation__isnull=False).distinct()
        else:
            # regular users see either everything that's published
            words = Keyword.objects.filter(text__istartswith=term,
                                            translation__gloss__inWeb__exact=True).distinct()

        try:
            crudetag = Tag.objects.get(name='lexis:crude')
        except:
            crudetag = None

        if safe and crudetag != None:

            crude = TaggedItem.objects.get_by_model(Gloss, crudetag)
            # remove crude words from result

            result = []
            for w in words:
                # remove word if all glosses for any translation are tagged crude
                trans = w.translation_set.all()
                glosses = [t.gloss for t in trans]

                if not all([g in crude for g in glosses]):
                    result.append(w)

            words = result


        if not category in ['all', '']:

            tag = Tag.objects.get(name=category)

            result = []
            for w in words:
                trans = w.translation_set.all()
                glosses = [t.gloss for t in trans]
                for g in glosses:
                    if tag in g.tags:
                        result.append(w)
            words = result


    else:
        term = ''
        words = []


    # display the keyword page if there's only one hit and it is an exact match
    if len(words) == 1 and words[0].text == term:
        return HttpResponseRedirect('/dictionary/words/'+words[0].text+'-1.html' )

    paginator = Paginator(words, 50)
    if request.GET.has_key('page'):

        page = request.GET['page']
        try:
            result_page = paginator.page(page)
        except PageNotAnInteger:
            result_page = paginator.page(1)
        except EmptyPage:
            result_page = paginator.page(paginator.num_pages)

    else:
        result_page = paginator.page(1)



    return render_to_response("dictionary/search_result.html",
                              {'query' : term,
                               'form': form,
                               'paginator' : paginator,
                               'wordcount' : len(words),
                               'page' : result_page,
                               'ANON_SAFE_SEARCH': settings.ANON_SAFE_SEARCH,
                               'ANON_TAG_SEARCH': settings.ANON_TAG_SEARCH,
                               'language': settings.LANGUAGE_NAME,
                               },
                              context_instance=RequestContext(request))



from django.db.models.loading import get_model, get_apps, get_models
from django.core import serializers

def keyword_value_list(request, prefix=None):
    """View to generate a list of possible values for
    a keyword given a prefix."""


    kwds = Keyword.objects.filter(text__startswith=prefix)
    kwds_list = [k.text for k in kwds]
    return HttpResponse("\n".join(kwds_list), content_type='text/plain')


def missing_video_list():
    """A list of signs that don't have an
    associated video file"""

    glosses = Gloss.objects.filter(inWeb__exact=True)
    for gloss in glosses:
        if not gloss.has_video():
            yield gloss

def missing_video_view(request):
    """A view for the above list"""

    glosses = missing_video_list()

    return render_to_response("dictionary/missingvideo.html",
                              {'glosses': glosses})

@login_required_config
def package(request):
    # Don't support small videos or since_timestamp for gloss changes (only video and images) at the moment

    first_part_of_file_name = 'signbank_pa'

    timestamp_part_of_file_name = str(int(time.time()))

    if 'since_timestamp' in request.GET:
        first_part_of_file_name += 'tch'
        since_timestamp = int(request.GET['since_timestamp'])
        timestamp_part_of_file_name = request.GET['since_timestamp']+'-'+timestamp_part_of_file_name
    else:
        first_part_of_file_name += 'ckage'
        since_timestamp = 0

    # TODO: Get IDs with this code GlossVideo.objects.filter(videofile='bsl-video/AM/AMERICA8.mp4').first().gloss.id

    glosses = signbank.tools.get_gloss_data()

    video_and_image_folder = settings.MEDIA_ROOT + "/" + settings.GLOSS_VIDEO_DIRECTORY + "/"

    archive_file_name = '.'.join([first_part_of_file_name,timestamp_part_of_file_name,'zip'])
    archive_file_path = settings.SIGNBANK_PACKAGES_FOLDER + archive_file_name

    video_urls = signbank.tools.get_static_urls_of_files(video_and_image_folder,'mp4',since_timestamp)
    image_urls = signbank.tools.get_static_urls_of_files(video_and_image_folder,'jpg',since_timestamp)

    collected_data = {'video_urls':video_urls,
                      'image_urls':image_urls,
                      'glosses':glosses}

    signbank.tools.create_zip_with_json_files(collected_data,archive_file_path)

    response = HttpResponse(FileWrapper(open(archive_file_path,'rb')), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename='+archive_file_name
    return response

def info(request):
    return HttpResponse(json.dumps([ settings.LANGUAGE_NAME, settings.COUNTRY_NAME ]), content_type='application/json')
