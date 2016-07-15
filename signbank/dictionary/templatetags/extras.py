from django.template import Library
from django.utils.safestring import mark_safe

register = Library()

@register.filter
def highlight(text, word):
    if str(text).startswith(word):
        return mark_safe("<b>%s</b>" % word + str(text)[len(word):])
    return text

