# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from future.builtins import int

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import urllib
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from mezzanine.accounts import get_profile_model
from mezzanine.generic.models import Rating
from mezzanine.utils.models import upload_to

from social_auth.backends.contrib.vk import VKOAuth2Backend

from workup.settings import MEDIA_ROOT


class UserProfile(models.Model):
    user = models.OneToOneField("auth.User")
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text=u"дд/мм/гггг",
        verbose_name=u"Дата рождения"
    )
    bio = models.TextField(null=True, blank=True, verbose_name=u"О себе")
    avatar = models.ImageField(
        verbose_name=u"Аватар",
        upload_to=upload_to("pubprofile.UserProfile.avatar", "avatar"),
        max_length=255,
        default=upload_to(
            "pubprofile.UserProfile.avatar",
            "avatar/default-avatar.jpg"
        )
    )
    karma = models.IntegerField(
        default=0,
        editable=False,
        verbose_name=u"Карма"
    )

    def __unicode__(self):
        return "%s (%s)" % (self.user, self.karma)


@receiver(post_save, sender=Rating)
@receiver(post_delete, sender=Rating)
def karma(sender, **kwargs):
    """
    Each time a rating is saved, check its value and modify the
    profile karma for the related object's user accordingly.
    Since ratings are either +1/-1, if a rating is being edited,
    we can assume that the existing rating is in the other direction,
    so we multiply the karma modifier by 2. We also run this when
    a rating is deleted (undone), in which case we just negate the
    rating value from the karma.
    """
    rating = kwargs["instance"]
    value = int(rating.value)
    if "created" not in kwargs:
        value *= -1  # Rating deleted
    elif not kwargs["created"]:
        value *= 2  # Rating changed
    content_object = rating.content_object
    if rating.user != content_object.user:
        queryset = get_profile_model().objects.filter(user=content_object.user)
        queryset.update(karma=models.F("karma") + value)


def get_user_avatar(backend, details, response, social_user, uid,
                    user, *args, **kwargs):
    url = None
    if backend.__class__ == VKOAuth2Backend:
        url = response['photo_max_orig']

    if url:
        profile = user.userprofile
        urllib.urlretrieve(url, MEDIA_ROOT+"/avatar/"+user.username+'.jpg')
        profile.avatar = "avatar/"+user.username+'.jpg'  # depends on where you saved it
        profile.save()
        user.email = response['email']
        user.save()
