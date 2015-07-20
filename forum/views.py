# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from future.builtins import super

from datetime import timedelta

from django.contrib.auth.models import User
from django.contrib.messages import info, error

from django.shortcuts import get_object_or_404, redirect
from django.utils.timezone import now
from django.http import HttpResponseRedirect, Http404
from django.views.generic import ListView, CreateView, DetailView,\
    TemplateView, UpdateView

from mezzanine.accounts import get_profile_model
from mezzanine.conf import settings
from mezzanine.generic.models import ThreadedComment, Keyword
from mezzanine.utils.views import paginate
from mezzanine.blog.models import BlogCategory
from mezzanine.blog.models import BlogPost

from workup.blog_extension.models import BlogImage
from workup.core_extension.utils import html_validator, order_by_score
from workup.core_extension.views import ScoreOrderingView
from workup.pubprofile.views import USER_PROFILE_RELATED_NAME, UserFilterView
from workup.forum.forms import TopicForm
from workup.forum.models import Topic


class TopicView(object):
    """
    List and detail view mixin for topics - just defines the correct
    queryset.
    """
    def get_queryset(self):
        return Topic.objects.published().select_related(
            "user",
            "user__%s" % USER_PROFILE_RELATED_NAME
        )


class TopicList(TopicView, ScoreOrderingView):
    """
    List view for topics, which can be for all users (homepage) or
    a single user (topics from user's profile page). Topics can be
    order by score (homepage, profile topics) or by most recently
    created ("newest" main nav item).
    """

    date_field = "publish_date"
    score_fields = ["rating_sum", "comments_count"]

    def get_context_data(self, **kwargs):
        context = super(TopicList, self).get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.all()
        return context

    def get_queryset(self):
        queryset = super(TopicList, self).get_queryset()
        tag = self.kwargs.get("tag")
        category = self.kwargs.get("category")
        if tag:
            queryset = queryset.filter(keywords__keyword__slug=tag)
        if category:
            queryset = queryset.filter(categories__slug=category)
        return queryset.prefetch_related("keywords__keyword")

    def get_title(self, context):
        tag = self.kwargs.get("tag")
        category = self.kwargs.get("category")
        if tag:
            return get_object_or_404(Keyword, slug=tag).title
        if context["by_score"]:
            return "Форум/Рейтинг"  # Homepage
        if category:
            return get_object_or_404(BlogCategory, slug=category).title
        if context["profile_user"]:
            return "Topics by %s" % getattr(
                context["profile_user"],
                USER_PROFILE_RELATED_NAME
            )
        else:
            return "Форум/Новые темы"


class TopicEdit(object):

    form_class = TopicForm
    model = Topic

    def get_context_data(self, **kwargs):
        context = super(TopicEdit, self).get_context_data(**kwargs)
        context["title"] = "Создание/Редактирование темы"
        context["images"] = BlogImage.objects.filter(user=self.request.user)
        return context

    def form_valid(self, form):
        form.instance.content = html_validator(form.instance.content)
        if not hasattr(form.instance, "user"):
            form.instance.user = self.request.user
            form.instance.gen_description = True
            info(self.request, "Тема создана")
        else:
            info(self.request, "Тема отредактирована")
        return super(TopicEdit, self).form_valid(form)


class TopicUpdate(TopicEdit, UpdateView):
    """
    Topic creation view - assigns the user to the new topic, as well
    as setting Mezzanine's ``gen_description`` attribute to ``False``,
    so that we can provide our own descriptions.
    """

    def get_object(self, queryset=None):
        topic = Topic.objects.get(id=self.kwargs['id'])
        if topic.is_editable(self.request):
            return topic
        else:
            raise Http404()


class TopicCreate(TopicEdit, CreateView):
    """
    Topic creation view - assigns the user to the new topic, as well
    as setting Mezzanine's ``gen_description`` attribute to ``False``,
    so that we can provide our own descriptions.
    """
    pass


class TopicDetail(TopicView, DetailView):
    """
    Topic detail view - threaded comments and rating are implemented
    in its template.
    """
    pass


class TagList(TemplateView):
    template_name = "topics/tag_list.html"
