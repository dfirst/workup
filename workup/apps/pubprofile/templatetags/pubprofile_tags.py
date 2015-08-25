from __future__ import unicode_literals

from mezzanine import template

from workup.pubprofile.views import USER_PROFILE_RELATED_NAME


register = template.Library()


@register.filter
def get_profile(user):
    """
    Returns the profile object associated with the given user.
    """
    return getattr(user, USER_PROFILE_RELATED_NAME)
