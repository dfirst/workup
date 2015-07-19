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
from workup.blog_extension.utils import html_validator
from workup.forum.forms import TopicForm
from workup.forum.models import Topic
from workup.forum.utils import order_by_score


# Returns the name to be used for reverse profile lookups from the user
# object. That's "profile" for the ``drum.topics.Profile``, but otherwise
# depends on the model specified in ``AUTH_PROFILE_MODULE``.
USER_PROFILE_RELATED_NAME = get_profile_model().user.field.related_query_name()


class UserFilterView(ListView):
    """
    List view that puts a ``profile_user`` variable into the context,
    which is optionally retrieved by a ``username`` urlpattern var.
    If a user is loaded, ``object_list`` is filtered by the loaded
    user. Used for showing lists of topics and comments.
    """

    def get_context_data(self, **kwargs):
        context = super(UserFilterView, self).get_context_data(**kwargs)
        try:
            username = self.kwargs["username"]
        except KeyError:
            profile_user = None
        else:
            users = User.objects.select_related(USER_PROFILE_RELATED_NAME)
            lookup = {"username__iexact": username, "is_active": True}
            profile_user = get_object_or_404(users, **lookup)
            qs = context["object_list"].filter(user=profile_user)
            context["object_list"] = qs
        context["profile_user"] = profile_user
        context["no_data"] = ("Whoa, there's like, literally no data here, "
                              "like seriously, I totally got nothin.")
        return context


class ScoreOrderingView(UserFilterView):
    """
    List view that optionally orders ``object_list`` by calculated
    score. Subclasses must defined a ``date_field`` attribute for the
    related model, that's used to determine time-scaled scoring.
    Ordering by score is the default behaviour, but can be
    overridden by passing ``False`` to the ``by_score`` arg in
    urlpatterns, in which case ``object_list`` is sorted by most
    recent, using the ``date_field`` attribute. Used for showing lists
    of topics and comments.
    """

    def get_context_data(self, **kwargs):
        context = super(ScoreOrderingView, self).get_context_data(**kwargs)
        qs = context["object_list"]
        context["by_score"] = self.kwargs.get("by_score", True)
        if context["by_score"]:
            qs = order_by_score(qs, self.score_fields, self.date_field)
        else:
            qs = qs.order_by("-" + self.date_field)
        context["object_list"] = paginate(qs, self.request.GET.get("page", 1),
                                          settings.ITEMS_PER_PAGE,
                                          settings.MAX_PAGING_LINKS)
        context["title"] = self.get_title(context)
        return context


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
        context['title'] = 'Создание/Редактирование темы'
        context['images'] = BlogImage.objects.filter(user=self.request.user)
        return context


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

    def form_valid(self, form):
        form.instance.content = html_validator(form.instance.content)
        info(self.request, "Тема отредактирована")
        return super(TopicUpdate, self).form_valid(form)


class TopicCreate(TopicEdit, CreateView):
    """
    Topic creation view - assigns the user to the new topic, as well
    as setting Mezzanine's ``gen_description`` attribute to ``False``,
    so that we can provide our own descriptions.
    """

    def form_valid(self, form):
        hours = getattr(settings, "ALLOWED_DUPLICATE_TOPIC_HOURS", None)
        if hours and form.instance.topic:
            lookup = {
                "topic": form.instance.topic,
                "publish_date__gt": now() - timedelta(hours=hours),
            }
            try:
                topic = Topic.objects.get(**lookup)
            except Topic.DoesNotExist:
                pass
            else:
                error(self.request, "Тема уже существует")
                return redirect(topic)
        form.instance.user = self.request.user
        form.instance.gen_description = True
        form.instance.content = html_validator(form.instance.content)
        info(self.request, "Тема создана")
        return super(TopicCreate, self).form_valid(form)


class TopicDetail(TopicView, DetailView):
    """
    Topic detail view - threaded comments and rating are implemented
    in its template.
    """
    pass


class CommentList(ScoreOrderingView):
    """
    List view for comments, which can be for all users ("comments" and
    "best" main nav items) or a single user (comments from user's
    profile page). Comments can be order by score ("best" main nav item)
    or by most recently created ("comments" main nav item, profile
    comments).
    """

    date_field = "submit_date"
    score_fields = ["rating_sum"]

    def get_queryset(self):
        qs = ThreadedComment.objects.filter(is_removed=False, is_public=True)
        select = ["user", "user__%s" % (USER_PROFILE_RELATED_NAME)]
        prefetch = ["content_object"]
        return qs.select_related(*select).prefetch_related(*prefetch)

    def get_title(self, context):
        if context["profile_user"]:
            return "Comments by %s" % getattr(
                context["profile_user"],
                USER_PROFILE_RELATED_NAME
            )
        elif context["by_score"]:
            return "Best comments"
        else:
            return "Latest comments"


class TagList(TemplateView):
    template_name = "topics/tag_list.html"


class BlogPostView(object):
    """
    List and detail view mixin for blogs - just defines the correct
    queryset.
    """
    def get_queryset(self):
        return BlogPost.objects.select_related(
            "user",
            "user__%s" % USER_PROFILE_RELATED_NAME
        )


class BlogPostList(BlogPostView, UserFilterView):
    """
    List view for blogs, which can be for a single user
    profile page).
    """
    def get_context_data(self, **kwargs):
        context = super(BlogPostList, self).get_context_data(**kwargs)
        context["drafts"] = context["object_list"].filter(status=1)
        context["object_list"] = paginate(
            context["object_list"].filter(status=2),
            self.request.GET.get("page", 1),
            settings.ITEMS_PER_PAGE, settings.MAX_PAGING_LINKS
        )
        return context
