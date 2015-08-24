from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.template import Context, Template

from mezzanine.conf import settings
from mezzanine.blog.models import BlogPost
from mezzanine.generic.models import ThreadedComment
from mezzanine.generic.forms import ThreadedCommentForm

from .forms import CommentEditForm

password = 'Tester'


class CommentsExtensionTest(TestCase):
    def setUp(self):
        User.objects.create_user(username='Tester_1',

                                 password=password
                                 )
        User.objects.create_user(username='Tester_2',
                                 email='test2@test.com',
                                 password=password
                                 )
        self.user = User.objects.get(pk=1)
        self.client_1 = Client()
        self.client_2 = Client()
        self.factory = RequestFactory()

    def test_comments_extension(self):
        # Create objects
        blog_post = BlogPost.objects.create(title='Post', user=self.user)
        content_type = ContentType.objects.get_for_model(blog_post)
        kwargs = {
            'content_type': content_type,
            'object_pk': blog_post.id,
            'site_id': settings.SITE_ID,
            'comment': 'Test comment for me',
            'user': self.user,
                  }
        for i in range(10):
            ThreadedComment.objects.create(**kwargs)
        # Test permissions for edit comment
        self.assertEqual(
            self.client_1.get(reverse('comment_edit_detail',
                                      kwargs={'pk': 1})).status_code, 302
        )
        self.client_1.post(
            reverse('login'),
            {'username': 'Tester_1', 'password': password}
        )
        self.assertEqual(
            self.client_1.get(reverse('comment_edit_detail',
                                      kwargs={'pk': 1})).status_code, 200
        )
        # Test comments owner
        self.client_2.post(
            reverse('login'),
            {'username': 'Tester_2', 'password': password}
        )
        self.assertEqual(
            self.client_2.get(reverse('comment_edit_detail',
                                      kwargs={'pk': 1})).status_code, 302
        )
        # Test display comments
        self.assertContains(
            self.client_1.get(reverse('blog_post_detail',
                                      kwargs={'slug': blog_post.slug})),
            'Test comment for me'
        )
        # Test comments edit form
        instance = ThreadedComment.objects.get(pk=1)
        security_data = CommentEditForm(
            {}, instance=instance).generate_security_data()
        security_hash = security_data['security_hash']
        timestamp = security_data['timestamp']
        self.client_1.post(reverse('comments-edit', args=(1,)),
                           {
                               'security_hash': security_hash,
                               'timestamp': timestamp,
                               'comment': 'Test BIG low'
                           })
        self.assertContains(
            self.client_1.get(reverse('blog_post_detail',
                                      kwargs={'slug': blog_post.slug})),
            'Test BIG low'
        )
        # Test comments form and required email
        request = self.factory.get(reverse('blog_create'))
        request.user = self.user
        security_data = ThreadedCommentForm(request,
                                            blog_post,
                                            kwargs).generate_security_data()
        security_hash = security_data['security_hash']
        timestamp = security_data['timestamp']
        kwargs = {
            'content_type': 'blog.blogpost',
            'object_pk': str(blog_post.id),
            'site_id': settings.SITE_ID,
            'security_hash': security_hash,
            'timestamp': timestamp,
            'comment': 'SSSS wwww EEEE',
            'name': self.user
                  }
        self.assertTrue(ThreadedCommentForm(request,
                                            blog_post,
                                            kwargs).is_valid())
        # Test comments_extension template tags
        test_template = Template('''
        {% load comments_generic comments_extension %}
        {% recent_comments_filter 5 as recent_comments %}
        <tag>{{recent_comments|length}}</tag>
        <tag>{% comment_edit_form_target comment %}</tag>
        {% get_comment_edit_form for comment as form %}
        {{ form }}
        ''').render(Context({'comment': instance}))
        self.assertIn('<tag>5</tag>', test_template)
        self.assertIn('<tag>/comments/edit/1/</tag>', test_template)
        self.assertIn('id="id_comment"', test_template)
