# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from future.builtins import super

from django.contrib.messages import info
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.views.generic import CreateView, DetailView,\
    TemplateView, UpdateView

from mezzanine.generic.models import Keyword, AssignedKeyword
from mezzanine.blog.models import BlogCategory

from workup.apps.blog_extension.models import BlogImage
from workup.apps.core_extension.utils import html_validator
from workup.apps.core_extension.views import ScoreOrderingView
from workup.apps.pubprofile.views import USER_PROFILE_RELATED_NAME
from .forms import TopicForm
from .models import Topic


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
        obj = form.save(commit=False)
        if not hasattr(obj, 'user'):
            obj.user = self.request.user
            info(self.request, "Тема создана")
        else:
            info(self.request, "Тема отредактирована")
        # filter for html content by Bleach
        obj.content = html_validator(obj.content)
        obj.save()
        # saving keywords
        keywords = Keyword.objects
        assigned_keywords = list()
        request_keywords = list(set(unicode(self.request.POST.get(
            'keywords_1', False)).replace(' ', '').split(',')))
        if len(request_keywords) >= 1:
            for keyword in request_keywords:
                keyword = keywords.filter(title=keyword)
                if len(keyword) >= 1:
                    assigned_keywords.append(
                        AssignedKeyword(keyword_id=keyword[0].id))
        obj.keywords = assigned_keywords
        # dirty solution to save category
        try:
            obj.categories = self.request.POST.getlist('categories', False)
        except:
            pass
        obj.save()
        return HttpResponseRedirect(
            reverse('topic_detail', kwargs={'slug': obj.slug}))


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
