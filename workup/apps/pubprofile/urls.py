from django.conf.urls import patterns, url

from workup.forum.views import TopicList
from workup.blog_extension.views import BlogPostList
from workup.comments_extension.views.generic import CommentList


urlpatterns = patterns(
    "",
    url("^users/(?P<username>.*)/topics/$",
        TopicList.as_view(
            template_name='accounts/account_profile_topics.html'),
        {"by_score": False},
        name="topic_list_user"),
    url("^users/(?P<username>.*)/blogs/$",
        BlogPostList.as_view(
            template_name='accounts/account_profile_blogs.html'),
        name="blog_list_user"),
    url("^users/(?P<username>.*)/comments/$",
        CommentList.as_view(
            template_name='accounts/account_profile_comments.html'),
        {"by_score": False},
        name="comment_list_user"),
)
