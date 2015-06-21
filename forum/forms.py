from django.conf import settings
from django.forms.models import modelform_factory
from django.forms import ValidationError

from workup.forum.models import Topic


BaseLinkForm = modelform_factory(Topic, fields=["title", "categories", "content"])


class TopicForm(BaseLinkForm):

    def clean(self):
        return self.cleaned_data