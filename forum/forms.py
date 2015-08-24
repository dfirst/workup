from django.forms.models import modelform_factory
from workup.forum.models import Topic


BaseTopicForm = modelform_factory(Topic,
                                  fields=["title", "categories",
                                          "content", "keywords"])


class TopicForm(BaseTopicForm):

    def clean(self):
        return self.cleaned_data
