from __future__ import unicode_literals

from django import template

from workup.pubprofile.views import USER_PROFILE_RELATED_NAME


register = template.Library()

@register.filter
def getvalue(mapping, key):
  return mapping.get(key, '')

@register.filter
def get_profile(user):
    """
    Returns the profile object associated with the given user.
    """
    return getattr(user, USER_PROFILE_RELATED_NAME)