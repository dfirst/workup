from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin
from django.db import connection

from mezzanine.core.admin import DisplayableAdmin
from .models import Topic


class TopicAdmin(DisplayableAdmin):

    list_display = ("id", "title", "status", "publish_date",
                    "user", "comments_count", "rating_sum")
    list_display_links = ("id",)
    list_editable = ()
    list_filter = ("status", "user__username")
    search_fields = ("title", "user__username", "user__email")
    ordering = ("-publish_date",)

    fieldsets = (
        (None, {
            "fields": ("title", "status", "publish_date", "user",
                       "description", "categories", "content", "keywords"),
        }),
    )


def delete_keywords(modeladmin, request, queryset):
    ids = ",".join(map(str, queryset.values_list("id", flat=True)))
    cursor = connection.cursor()
    cursor.execute("DELETE FROM generic_assignedkeyword "
                   "WHERE keyword_id IN (%s);" % ids)
    cursor.execute("DELETE FROM generic_keyword WHERE id IN (%s);" % ids)


class KeywordAdmin(admin.ModelAdmin):

    ordering = ["title"]
    list_display = ["id", "title", "slug"]
    list_editable = ["title", "slug"]
    actions = [delete_keywords]

    class Media:
        css = {"all": ["css/keywords.css"]}

    def get_actions(self, request):
        actions = super(KeywordAdmin, self).get_actions(request)
        actions.pop("delete_selected")
        return actions


admin.site.register(Topic, TopicAdmin)

if getattr(settings, "AUTO_TAG", False):
    from mezzanine.generic.models import Keyword
    admin.site.register(Keyword, KeywordAdmin)
