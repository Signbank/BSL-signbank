from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.db.models import Q
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
import datetime
import csv
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom

from signbank.dictionary.models import *
from signbank.dictionary.forms import *
from signbank.feedback.models import *
from signbank.video.forms import VideoUploadForGlossForm
from tagging.models import Tag, TaggedItem

class GlossListView(ListView):

    model = Gloss
    template_name = 'dictionary/admin_gloss_list.html'
    paginate_by = 10
    only_export_ecv = False #Used to call the 'export ecv' functionality of this view without the need for an extra GET parameter

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(GlossListView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['searchform'] = GlossSearchForm(self.request.GET)
        context['glosscount'] = Gloss.objects.all().count()
        context['add_gloss_form'] = GlossCreateForm()
        context['ADMIN_RESULT_FIELDS'] = settings.ADMIN_RESULT_FIELDS
        return context


    def get_paginate_by(self, queryset):
        """
        Paginate by specified value in querystring, or use default class property value.
        """
        return self.request.GET.get('paginate_by', self.paginate_by)


    def render_to_response(self, context):
        # Look for a 'format=json' GET argument
        if self.request.GET.get('format') == 'CSV':
            return self.render_to_csv_response(context)
        elif self.request.GET.get('export_ecv') == 'ECV' or self.only_export_ecv:
            return self.render_to_ecv_export_response(context)
        else:
            return super(GlossListView, self).render_to_response(context)

    def render_to_ecv_export_response(self, context):
        description  = 'DESCRIPTION'
        language     = 'LANGUAGE'
        lang_ref     = 'LANG_REF'

        cv_entry_ml  = 'CV_ENTRY_ML'
        cve_id       = 'CVE_ID'
        cve_value    = 'CVE_VALUE'

        topattributes = {'xmlns:xsi':"http://www.w3.org/2001/XMLSchema-instance",
                         'DATE':str(datetime.date.today())+ 'T'+str(datetime.datetime.now().time()),
                         'AUTHOR':'',
                         'VERSION':'0.2',
                         'xsi:noNamespaceSchemaLocation':"http://www.mpi.nl/tools/elan/EAFv2.8.xsd"}
        top = ET.Element('CV_RESOURCE', topattributes)

        for lang in settings.ECV_SETTINGS['languages']:
            ET.SubElement(top, language, lang['attributes'])

        cv_element = ET.SubElement(top, 'CONTROLLED_VOCABULARY', {'CV_ID':settings.ECV_SETTINGS['CV_ID']})

        # description for cv_element
        for lang in settings.ECV_SETTINGS['languages']:
            myattributes = {lang_ref: lang['id']}
            desc_element = ET.SubElement(cv_element, description, myattributes)
            desc_element.text = lang['description']

        # TODO: instead of Gloss.objects this was Gloss.none_morpheme_objects
        for gloss in Gloss.objects.filter(excludeFromEcv=False):
            glossid = str(gloss.pk)
            myattributes = {cve_id: glossid, 'EXT_REF':'signbank-ecv'}
            cve_entry_element = ET.SubElement(cv_element, cv_entry_ml, myattributes)

            for lang in settings.ECV_SETTINGS['languages']:
                langId = lang['id']
                if len(langId) == 3:
                    langId = [c[2] for c in settings.LANGUAGE_CODE_MAP if c[3] == langId][0]
                desc = self.get_ecv_descripion_for_gloss(gloss, langId, settings.ECV_SETTINGS['include_phonology_and_frequencies'])
                cve_value_element = ET.SubElement(cve_entry_element, cve_value, {description:desc, lang_ref:lang['id']})
                cve_value_element.text = self.get_value_for_ecv(gloss, lang['annotation_idgloss_fieldname'])

        ET.SubElement(top, 'EXTERNAL_REF', {'EXT_REF_ID':'signbank-ecv', 'TYPE':'resource_url', 'VALUE': settings.URL + "/dictionary/gloss/"})

        xmlstr = minidom.parseString(ET.tostring(top,'utf-8')).toprettyxml(indent="   ")
        import codecs
        with codecs.open(settings.ECV_FILE, "w", "utf-8") as f:
            f.write(xmlstr)

#        tree = ET.ElementTree(top)
#        tree.write(open(settings.ECV_FILE, 'w'), encoding ="utf-8",xml_declaration=True, method="xml")

        return HttpResponse('OK')

    def get_ecv_descripion_for_gloss(self, gloss, lang, include_phonology_and_frequencies=False):
        desc = ""
        # TODO: Add support for ECV phonology and frequencies
        # if include_phonology_and_frequencies:
        #     description_fields = ['handedness','domhndsh', 'subhndsh', 'handCh', 'locprim', 'relOriMov', 'movDir','movSh', 'tokNo',
        #                   'tokNoSgnr']
        #
        #     for f in description_fields:
        #         if f in settings.FIELDS['phonology']:
        #             choice_list = FieldChoice.objects.filter(field__iexact=fieldname_to_category(f))
        #             machine_value = getattr(gloss,f)
        #             value = machine_value_to_translated_human_value(machine_value,choice_list,lang)
        #             if value is None:
        #                 value = ' '
        #         else:
        #             value = self.get_value_for_ecv(gloss,f)
        #
        #         if f == 'handedness':
        #             desc = value
        #         elif f == 'domhndsh':
        #             desc = desc+ ', ('+ value
        #         elif f == 'subhndsh':
        #             desc = desc+','+value
        #         elif f == 'handCh':
        #             desc = desc+'; '+value+')'
        #         elif f == 'tokNo':
        #             desc = desc+' ['+value
        #         elif f == 'tokNoSgnr':
        #             desc = desc+'/'+value+']'
        #         else:
        #             desc = desc+', '+value

        if desc:
            desc += ", "

        trans = [t.translation.text for t in gloss.translation_set.all()]
        desc += ", ".join(
            # The next line was adapted from an older version of this code,
            # that happened to do nothing. I left this for future usage.
            #map(lambda t: str(t.encode('ascii','xmlcharrefreplace')) if isinstance(t, unicode) else t, trans)
            trans
        )

        return desc

    def get_value_for_ecv(self, gloss, fieldname):
        try:
            value = getattr(gloss, 'get_'+fieldname+'_display')()

        except AttributeError:
            value = getattr(gloss,fieldname)

        # This was disabled with the move to python 3... might not be needed anymore
        # if isinstance(value,unicode):
        #     value = str(value.encode('ascii','xmlcharrefreplace'))

        if value is None:
           value = " "
        elif not isinstance(value,str):
            value = str(value)

        if value == '-':
            value = ' '
        return value

    def render_to_csv_response(self, context):

        if not self.request.user.has_perm('dictionary.export_csv'):
            raise PermissionDenied

        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="dictionary-export.csv"'


        fields = [f.name for f in Gloss._meta.fields]


        writer = csv.writer(response)
        header = [Gloss._meta.get_field(f).verbose_name for f in fields]
        header.append("Keywords")
        header.append("Tags")
        if self.request.user.has_perm('dictionary.view_advanced_properties'):
            # Find out how many extra rows there are for notes
            note_count = 0
            for gloss in self.get_queryset():
                new_max = gloss.definition_set.count()
                if new_max > note_count:
                    note_count = new_max
            # Add headers for them
            for _ in range(note_count):
                header.append("Note ID")
                header.append("Note Published")
                header.append("Note Role")
                header.append("Note Text")
        writer.writerow(header)


        for gloss in self.get_queryset():
            row = []
            for f in fields:
                row.append(getattr(gloss, f))

            # get translations
            trans = [t.translation.text for t in gloss.translation_set.all()]
            row.append(", ".join(trans))

            # get tags
            tags = [t.name for t in gloss.tags.all()]
            row.append(", ".join(tags))

            # Add definitions/notes
            if self.request.user.has_perm('dictionary.view_advanced_properties'):
                count = 0
                for defi in gloss.definition_set.all():
                    count += 1
                    if defi.published or self.request.user.has_perm('dictionary.can_view_unpub_defs'):
                        row.append(str(count))
                        if defi.published:
                            row.append("Published")
                        else:
                            row.append("Unpublished")
                        rd = defi.get_role_display()
                        row.append(string.replace(rd, ';', ','))
                        row.append(string.replace(defi.text, ';', ','))

            # Make it safe for non-ascii
            safe_row = [];
            for column in row:
                try:
                    safe_row.append(''.join([i if ord(i) < 128 else ' ' for i in str(column)]))
                except AttributeError:
                    safe_row.append(None);

            writer.writerow(safe_row)

        return response


    def get_queryset(self):

        # get query terms from self.request
        qs = Gloss.objects.all()

        #print "QS:", len(qs)

        get = self.request.GET


        if get.has_key('search') and get['search'] != '':
            val = get['search']
            query = Q(idgloss__istartswith=val) | \
                    Q(annotation_idgloss__istartswith=val)

            if re.match('^\d+$', val):
                query = query | Q(sn__exact=val)

            qs = qs.filter(query)
            #print "A: ", len(qs)

        if get.has_key('keyword') and get['keyword'] != '':
            val = get['keyword']
            qs = qs.filter(translation__translation__text__istartswith=val)


        if get.has_key('inWeb') and get['inWeb'] != 'unspecified':
            val = get['inWeb'] == 'yes'
            qs = qs.filter(inWeb__exact=val)
            #print "B :", len(qs)


        if get.has_key('hasvideo') and get['hasvideo'] != 'unspecified':
            val = get['hasvideo'] == 'no'

            qs = qs.filter(glossvideo__isnull=val)

        if get.has_key('defspublished') and get['defspublished'] != 'unspecified':
            val = get['defspublished'] == 'yes'

            qs = qs.filter(definition__published=val)


        ## phonology field filters
        if get.has_key('domhndsh') and get['domhndsh'] != '':
            val = get['domhndsh']
            qs = qs.filter(domhndsh__exact=val)

            #print "C :", len(qs)

        if get.has_key('subhndsh') and get['subhndsh'] != '':
            val = get['subhndsh']
            qs = qs.filter(subhndsh__exact=val)
            #print "D :", len(qs)

        if get.has_key('final_domhndsh') and get['final_domhndsh'] != '':
            val = get['final_domhndsh']
            qs = qs.filter(final_domhndsh__exact=val)
            #print "E :", len(qs)

        if get.has_key('final_subhndsh') and get['final_subhndsh'] != '':
            val = get['final_subhndsh']
            qs = qs.filter(final_subhndsh__exact=val)
           # print "F :", len(qs)

        if get.has_key('locprim') and get['locprim'] != '':
            val = get['locprim']
            qs = qs.filter(locprim__exact=val)
            #print "G :", len(qs)

        if get.has_key('locsecond') and get['locsecond'] != '':
            val = get['locsecond']
            qs = qs.filter(locsecond__exact=val)

            #print "H :", len(qs)

        if get.has_key('final_loc') and get['final_loc'] != '':
            val = get['final_loc']
            qs = qs.filter(final_loc__exact=val)



        if get.has_key('initial_relative_orientation') and get['initial_relative_orientation'] != '':
            val = get['initial_relative_orientation']
            qs = qs.filter(initial_relative_orientation__exact=val)

        if get.has_key('final_relative_orientation') and get['final_relative_orientation'] != '':
            val = get['final_relative_orientation']
            qs = qs.filter(final_relative_orientation__exact=val)

        if get.has_key('initial_palm_orientation') and get['initial_palm_orientation'] != '':
            val = get['initial_palm_orientation']
            qs = qs.filter(initial_palm_orientation__exact=val)

        if get.has_key('final_palm_orientation') and get['final_palm_orientation'] != '':
            val = get['final_palm_orientation']
            qs = qs.filter(final_palm_orientation__exact=val)

        if get.has_key('initial_secondary_loc') and get['initial_secondary_loc'] != '':
            val = get['initial_secondary_loc']
            qs = qs.filter(initial_secondary_loc__exact=val)

        if get.has_key('final_secondary_loc') and get['final_secondary_loc'] != '':
            val = get['final_secondary_loc']
            qs = qs.filter(final_secondary_loc__exact=val)

           # print "G :", len(qs)
        # end of phonology filters


        if get.has_key('defsearch') and get['defsearch'] != '':

            val = get['defsearch']

            if get.has_key('defrole'):
                role = get['defrole']
            else:
                role = 'all'

            if role == 'all':
                qs = qs.filter(definition__text__icontains=val)
            else:
                qs = qs.filter(definition__text__icontains=val, definition__role__exact=role)




        vals = get.getlist('dialect', [])
        if vals != []:
            qs = qs.filter(dialect__in=vals)

           # print "H :", len(qs)

        vals = get.getlist('language', [])
        if vals != []:
            qs = qs.filter(language__in=vals)

            #print "I :", len(qs)

        if get.has_key('tags') and get['tags'] != '':
            vals = get.getlist('tags')

            tags = []
            for t in vals:
                tags.extend(Tag.objects.filter(name=t))


            # search is an implicit AND so intersection
            tqs = TaggedItem.objects.get_intersection_by_model(Gloss, tags)

            # intersection
            qs = qs & tqs

            #print "J :", len(qs)

        qs = qs.distinct()

        if get.has_key('nottags') and get['nottags'] != '':
            vals = get.getlist('nottags')

           # print "NOT TAGS: ", vals

            tags = []
            for t in vals:
                tags.extend(Tag.objects.filter(name=t))

            # search is an implicit AND so intersection
            tqs = TaggedItem.objects.get_intersection_by_model(Gloss, tags)

           # print "NOT", tags, len(tqs)
            # exclude all of tqs from qs
            qs = [q for q in qs if q not in tqs]

           # print "K :", len(qs)


       # print "Final :", len(qs)
        return qs




class GlossDetailView(DetailView):

    model = Gloss
    context_object_name = 'gloss'


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(GlossDetailView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['tagform'] = TagUpdateForm()
        context['videoform'] = VideoUploadForGlossForm()
        context['definitionform'] = DefinitionForm()
        context['relationform'] = RelationForm()
        context['navigation'] = context['gloss'].navigation(True)
        context['interpform'] = InterpreterFeedbackForm()
        context['SIGN_NAVIGATION']  = settings.SIGN_NAVIGATION
        if settings.SIGN_NAVIGATION:
            context['glosscount'] = Gloss.objects.count()
            context['glossposn'] =  Gloss.objects.filter(sn__lt=context['gloss'].sn).count()+1
        return context


def gloss_ajax_complete(request, prefix):
    """Return a list of glosses matching the search term
    as a JSON structure suitable for typeahead."""


    query = Q(idgloss__istartswith=prefix) | \
            Q(annotation_idgloss__istartswith=prefix) | \
            Q(sn__startswith=prefix)
    qs = Gloss.objects.filter(query)

    result = []
    for g in qs:
        result.append({'idgloss': g.idgloss, 'annotation_idgloss': g.annotation_idgloss, 'sn': g.sn, 'pk': "%s (%s)" % (g.idgloss, g.pk)})

    return HttpResponse(json.dumps(result), {'content-type': 'application/json'})
