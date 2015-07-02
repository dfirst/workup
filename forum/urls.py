from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from workup.forum.views import TopicList, TopicCreate, TopicDetail, CommentList, TagList, TopicUpdate, BlogPostList


urlpatterns = patterns("",
    url("^forum/$",
        TopicList.as_view(), {"by_score": False},
        name="topic_list_latest"),
    url("^forum/best/$",
        TopicList.as_view(),
        name="topic_list_best"),
    url("^forum/tags/(?P<tag>.*)/$",
        TopicList.as_view(),
        name="topic_list_tag"),
    url("^forum/category/(?P<category>.*)/$",
        TopicList.as_view(), {"by_score": False},
        name="topic_list_category"),
    url("^forum/create/$",
        login_required(TopicCreate.as_view()),
        name="topic_create"),
    url("^forum/edit/(?P<id>.*)/$",
        login_required(TopicUpdate.as_view()),
        name="topic_edit"),
    url("^forum/(?P<slug>.*)/$",
        TopicDetail.as_view(),
        name="topic_detail"),
    url("^users/(?P<username>.*)/topics/$",
        TopicList.as_view(template_name = 'accounts/account_profile_topics.html'), {"by_score": False},
        name="topic_list_user"),
    url("^users/(?P<username>.*)/comments/$",
        CommentList.as_view(template_name = 'accounts/account_profile_comments.html'), {"by_score": False},
        name="comment_list_user"),
    url("^comments/$",
        CommentList.as_view(), {"by_score": False},
        name="comment_list_latest"),
    url("^best/$",
        CommentList.as_view(),
        name="comment_list_best"),
    url("^tags/$",
        TagList.as_view(),
        name="tag_list"),
    url("^users/(?P<username>.*)/blogs/$",
        BlogPostList.as_view(template_name='accounts/account_profile_blogs.html'), name="blog_list_user"),
)