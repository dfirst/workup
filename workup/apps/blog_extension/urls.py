from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import BlogCreate, BlogUpdate, upload, upload_delete


urlpatterns = patterns(
    "",
    url("^blog/create/$",
        login_required(BlogCreate.as_view()),
        name="blog_create"),
    url("^blog/edit/(?P<id>.*)/$",
        login_required(BlogUpdate.as_view()),
        name="blog_edit"),
    url('^blog/upload/', upload, name='jfu_upload'),
    url('^blog/delete/(?P<pk>\d+)$', upload_delete, name='jfu_delete'),
)
