from django.conf.urls import patterns, url

from .views.moderation import CommentDetail
from .views.generic import CommentList


urlpatterns = patterns(
    "workup.apps.comments_extension.views",
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
    url("^comments/best/$",
        CommentList.as_view(),
        name="comment_list_best"),
)
