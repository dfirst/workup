from __future__ import unicode_literals

from collections import defaultdict
from mezzanine import template
from django.template.defaultfilters import timesince

from workup.forum.utils import order_by_score
from workup.forum.views import CommentList, USER_PROFILE_RELATED_NAME

from mezzanine.generic.models import ThreadedComment

register = template.Library()


@register.filter
def get_profile(user):
    """
    Returns the profile object associated with the given user.
    """
    return getattr(user, USER_PROFILE_RELATED_NAME)


@register.simple_tag(takes_context=True)
def order_comments_by_score_for(context, topic):
    """
    Preloads threaded comments in the same way Mezzanine initially does,
    but here we order them by score.
    """
    comments = defaultdict(list)
    qs = topic.comments.visible().select_related(
        "user",
        "user__%s" % (USER_PROFILE_RELATED_NAME)
    )
    for comment in order_by_score(qs, CommentList.score_fields, "submit_date"):
        comments[comment.replied_to_id].append(comment)
    context["all_comments"] = comments
    return ""


@register.filter
def short_timesince(date):
    return timesince(date).split(",")[0]

@register.as_tag
def recent_comments_filter(limit=5):
    """
    Put a list of recently published blog posts into the template
    context. A tag title or slug, category title or slug or author's
    username can also be specified to filter the recent posts returned.

    Usage::

        {% blog_recent_posts 5 as recent_posts %}
        {% blog_recent_posts limit=5 tag="django" as recent_posts %}
        {% blog_recent_posts limit=5 category="python" as recent_posts %}
        {% blog_recent_posts 5 username=admin as recent_posts %}

    """
    recent_comments = ThreadedComment.objects.all().select_related("user")
    return list(recent_comments)[-limit:]