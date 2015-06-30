from django import forms
from django.forms.models import modelform_factory
from mezzanine.blog.models import BlogPost


BaseBlogForm = modelform_factory(BlogPost, fields=["title", "content", "status", "gen_description", "allow_comments", "categories", "featured_image"])


class CreateBlogForm(BaseBlogForm):
    featured_image = forms.CharField()
    def clean(self):
        return self.cleaned_data

