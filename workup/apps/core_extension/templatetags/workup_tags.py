from __future__ import unicode_literals

from django.template.defaultfilters import timesince

from mezzanine import template

register = template.Library()


@register.filter
def getvalue(mapping, key):
    return mapping.get(key, '')


@register.filter
def short_timesince(date):
    return timesince(date).split(",")[0]
