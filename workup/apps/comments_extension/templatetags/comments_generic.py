from __future__ import unicode_literals

from collections import defaultdict
from mezzanine import template
from mezzanine.generic.models import ThreadedComment

from workup.apps.core_extension.utils import order_by_score
from workup.apps.comments_extension.views.generic import CommentList, USER_PROFILE_RELATED_NAME


register = template.Library()


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


@register.as_tag
def recent_comments_filter(limit=5):
    """
    Put a list of recently published blog posts into the template
    context. A tag title or slug, category title or slug or author's
    username can also be specified to filter the recent posts returned.

    Usage::

        {% recent_comments_filter 5 as recent_comments %}
        {% recent_comments_filter limit=5 tag="django" as recent_comments %}
        {% recent_comments_filter limit=5 category="python" as recent_comments %}
        {% recent_comments_filter 5 username=admin as recent_comments %}

    """
    recent_comments = ThreadedComment.objects.all().select_related("user")
    return list(recent_comments)[-limit:]
