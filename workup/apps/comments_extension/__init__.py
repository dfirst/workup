from __future__ import absolute_import
from django.core import urlresolvers
import django_comments
from .forms import CommentEditForm


def get_edit_form():
    """
    Returns a (new) comment edit form object
    """
    if django_comments.get_comment_app_name() != django_comments.DEFAULT_COMMENTS_APP and \
            hasattr(django_comments.get_comment_app(), "get_edit_form"):
        return django_comments.get_comment_app().get_edit_form()
    else:
        return CommentEditForm


def get_edit_modelform(comment):
    """
    Returns the comment ModelForm instance
    """
    if django_comments.get_comment_app_name() != django_comments.DEFAULT_COMMENTS_APP and \
            hasattr(django_comments.get_comment_app(), "get_edit_modelform"):
        return django_comments.get_comment_app().get_edit_modelform()
    else:
        return CommentEditForm(instance=comment)


def get_edit_form_target(comment):
    """
    Returns the target URL for the comment edit form submission view.
    """
    if django_comments.get_comment_app_name() != django_comments.DEFAULT_COMMENTS_APP and \
            hasattr(django_comments.get_comment_app(), "get_edit_form_target"):
        return django_comments.get_comment_app().get_edit_form_target()
    else:
        return urlresolvers.reverse("workup.apps.comments_extension.views.moderation.edit", args=(comment.id,))
