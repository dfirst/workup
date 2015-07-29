# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from future.builtins import super
import magic

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.views.generic import CreateView, UpdateView
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.messages import info

from mezzanine.conf import settings
from mezzanine.blog.models import BlogPost
from mezzanine.utils.views import paginate
from mezzanine.generic.models import AssignedKeyword, Keyword
from jfu.http import upload_receive, UploadResponse, JFUResponse

from workup.core_extension.utils import html_validator
from workup.pubprofile.views import USER_PROFILE_RELATED_NAME, UserFilterView
from .forms import CreateBlogForm
from .models import BlogImage


class BlogActView(object):
    model = BlogPost
    form_class = CreateBlogForm
    template_name = 'blog_create.html'

    def get_context_data(self, **kwargs):
        context = super(BlogActView, self).get_context_data(**kwargs)
        context['title'] = 'Создание/Редактирование записи'
        context['images'] = BlogImage.objects.filter(
            user=self.request.user,
            status=2
        )
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.featured_image = self.request.POST.get('featured_image', False).replace('/static/media/', '').strip()
        if not hasattr(obj, 'user'):
            obj.user = self.request.user
        # filter for html content by Bleach
        obj.content = html_validator(obj.content)
        obj.save()
        # dirty solution to save keywords
        keywords = Keyword.objects
        assigned_keywords = list()
        request_keywords = list(set(unicode(self.request.POST.get('keywords_1', False)).replace(' ','').split(',')))
        if len(request_keywords)>=1:
            for keyword in request_keywords:
                keyword = keywords.filter(title=keyword)
                if len(keyword)>=1:
                    assigned_keywords.append(AssignedKeyword(keyword_id=keyword[0].id))
        obj.keywords = assigned_keywords
        # dirty solution to save category
        try:
            obj.categories = self.request.POST.getlist('categories', False)
        except:
            pass
        obj.save()
        if obj.status == 1:
            info(self.request, "Черновик сохранен")
            return HttpResponseRedirect(
                reverse(
                    'blog_list_user', kwargs={'username': self.request.user}
                )
            )
        elif obj.status == 2:
            info(self.request, "Запись сохранена")
            return HttpResponseRedirect(reverse('blog_post_detail', kwargs={'slug': obj.slug}))


class BlogCreate(BlogActView, CreateView):
    pass


class BlogUpdate(BlogActView, UpdateView):
    """
    Topic creation view - assigns the user to the new topic, as well
    as setting Mezzanine's ``gen_description`` attribute to ``False``,
    so that we can provide our own descriptions.
    """
    def get_object(self, queryset=None):
        blog_object = BlogPost.objects.get(id=self.kwargs['id'])
        if blog_object.is_editable(self.request):
            return blog_object
        else:
            raise Http404()


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


@login_required
@require_POST
def upload(request):

    # The assumption here is that jQuery File Upload
    # has been configured to send files one at a time.
    # If multiple files can be uploaded simulatenously,
    # 'file' may be a list of files.

    file = upload_receive(request)

    if 'image' not in magic.from_buffer(file.read(), mime=True) or file.size > 1024*1024*1.5:
        raise ValidationError()

    instance = BlogImage(image=file, user=request.user)
    instance.status = 2
    instance.save()

    basename = instance.image.name

    file_dict = {
        'name': basename,
        'size': file.size,

        'url': settings.MEDIA_URL + basename,
        'thumbnailUrl': settings.MEDIA_URL + basename,

        'deleteUrl': reverse('jfu_delete', kwargs={'pk': instance.pk}),
        'deleteType': 'POST',
    }
    return UploadResponse(request, file_dict)


@login_required
@require_POST
def upload_delete(request, pk):
    success = True
    try:
        instance = BlogImage.objects.get(pk=pk)
        if instance.is_editable(request):
            instance.status = 1
            instance.save()
        else:
            raise Http404()
    except BlogImage.DoesNotExist:
        success = False

    return JFUResponse(request, success)
