import time
from django import forms
from django.conf import settings
from django.utils.text import get_text_list
from django.utils.translation import ungettext, ugettext, ugettext_lazy as _
from django.forms.util import ErrorDict
from django.utils.crypto import salted_hmac, constant_time_compare

from workup.comments_extension import django_comments


class CommentEditForm(forms.ModelForm):
    """
    ModelForm for editing existing comments.
    Quacks like the CommentSecurityForm in django.contrib.comments.forms
    """
    def __init__(self, *args, **kwargs):
        super(CommentEditForm, self).__init__(*args, **kwargs)

        # initiate the form with security data
        self.initial.update(self.generate_security_data())

    comment = forms.CharField(
        label=_("Comment"),
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        max_length=django_comments.forms.COMMENT_MAX_LENGTH)

    # Security fields
    timestamp = forms.IntegerField(widget=forms.HiddenInput)
    security_hash = forms.CharField(
        min_length=40, max_length=40, widget=forms.HiddenInput
    )

    class Meta:
        model = django_comments.models.Comment
        fields = ("comment", "timestamp", "security_hash")

    def security_errors(self):
        """
        Return the errors associated with security
        """
        errors = ErrorDict()
        for f in ["timestamp", "security_hash"]:
            if f in self.errors:
                errors[f] = self.errors[f]
        return errors

    def generate_security_data(self):
        """
        Generate initial security data
        """
        # Use the original timestamp
        timestamp = str(
            int(time.mktime(self.instance.submit_date.timetuple()))
        )
        security_dict = {
            "content_type": str(self.instance.content_type.pk),
            "object_pk": str(self.instance.pk),
            "timestamp": timestamp,
            "security_hash": self.initial_security_hash(timestamp)
        }
        return security_dict

    def initial_security_hash(self, timestamp):
        """
        Generate the initial security hash from self.content_object
        and a (unix) timestamp.
        """
        initial_security_dict = {
            "content_type": str(self.instance.content_type.pk),
            "object_pk": str(self.instance.pk),
            "timestamp": timestamp
        }
        return self.generate_security_hash(**initial_security_dict)

    def generate_security_hash(self, content_type, object_pk, timestamp):
        """
        Generate a HMAC security hash from the provided info.
        """
        info = (content_type, object_pk, timestamp)
        key_salt = "workup.comments_extension.forms.CommentEditForm"
        value = "-".join(info)
        return salted_hmac(key_salt, value).hexdigest()

    #
    # Clean methods
    #
    def clean_security_hash(self):
        """
        Make sure the security hash match
        """
        timestamp = str(
            int(time.mktime(self.instance.submit_date.timetuple()))
        )
        security_hash_dict = {
            "content_type": self.data.get("content_type", str(self.instance.content_type.pk)),
            "object_pk": self.data.get("object_pk", str(self.instance.pk)),
            "timestamp": self.data.get("timestamp", timestamp)
        }
        expected_hash = self.generate_security_hash(**security_hash_dict)
        actual_hash = self.cleaned_data["security_hash"]
        if not constant_time_compare(expected_hash, actual_hash):
            raise forms.ValidationError("Security hash check failed.")
        return actual_hash

    def clean_comment(self):
        """
        If COMMENTS_ALLOW_PROFANITIES is False, check that the comment doesn't
        contain anything in PROFANITIES_LIST.
        """
        comment = self.cleaned_data["comment"]
        if settings.COMMENTS_ALLOW_PROFANITIES is False:
            bad_words = [
                w for w in settings.PROFANITIES_LIST if w in comment.lower()
            ]
            if bad_words:
                raise forms.ValidationError(ungettext(
                    "Watch your mouth! The word %s is not allowed here.",
                    "Watch your mouth! The words %s are not allowed here.",
                    len(bad_words)) % get_text_list(
                        ["'%s%s%s'" % (i[0], "-" * (len(i) - 2), i[-1])
                         for i in bad_words], ugettext("and")))
        return comment
