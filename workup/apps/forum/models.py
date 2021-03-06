# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from re import sub, split
from operator import ior

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.models import Displayable, Ownable, RichText
from mezzanine.generic.models import Keyword, AssignedKeyword
from mezzanine.generic.fields import RatingField, CommentsField
from mezzanine.blog.models import BlogCategory

USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class Topic(Displayable, Ownable, RichText):

    categories = models.ManyToManyField(BlogCategory,
                                        verbose_name=_("Categories"),
                                        blank=True, related_name="topics")
    rating = RatingField()
    comments = CommentsField()

    def get_absolute_url(self):
        return reverse("topic_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        keywords = []
        if not self.keywords_string and getattr(settings, "AUTO_TAG", False):
            variations = lambda word: [
                word,
                sub("^([^A-Za-z0-9])*|([^A-Za-z0-9]|s)*$", "", word),
                sub("^([^A-Za-z0-9])*|([^A-Za-z0-9])*$", "", word)
            ]
            keywords = sum(map(variations, split("\s|/", self.title)), [])
        super(Topic, self).save(*args, **kwargs)
        if keywords:
            lookup = reduce(ior, [Q(title__iexact=k) for k in keywords])
            for keyword in Keyword.objects.filter(lookup):
                self.keywords.add(AssignedKeyword(keyword=keyword))

    class Meta:
        app_label = "forum"
