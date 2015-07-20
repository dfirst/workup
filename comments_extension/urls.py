from django.conf.urls import patterns, url

from workup.comments_extension.views.moderation import CommentDetail
from workup.comments_extension.views.generic import CommentList


urlpatterns = patterns(
    "workup.comments_extension.views",
    url(r"^edit/(\d+)/$", view="moderation.edit",
        name="comments-edit"
        ),
    url(r"^edited/$", view="moderation.edit_done",
        name="comments-edit-done"
        ),
    url(r"^editing/(?P<pk>.*)/$", CommentDetail.as_view(),
        name="comment_edit_detail"
        ),
    url("^comments/$",
        CommentList.as_view(), {"by_score": False},
        name="comment_list_latest"),
    url("^best/$",
        CommentList.as_view(),
        name="comment_list_best"),
    url("^users/(?P<username>.*)/comments/$",
        CommentList.as_view(template_name='accounts/account_profile_comments.html'), {"by_score": False},
        name="comment_list_user"),
)
