import os
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from mezzanine.blog.models import BlogPost
from mezzanine.generic.models import Keyword

password = 'Tester'


class BlogExtensionTest(TestCase):
    def setUp(self):
        User.objects.create_user(username='Tester_1',
                                 email='test1@test.com',
                                 password=password
                                 )
        User.objects.create_user(username='Tester_2',
                                 email='test2@test.com',
                                 password=password
                                 )
        self.client_1 = Client()
        self.client_2 = Client()

    def test_blog_extension(self):
        # Auth required test
        self.assertEqual(
            self.client_1.get(reverse('blog_create')).status_code, 302
        )
        self.client_1.post(
            reverse('login'),
            {'username': 'Tester_1', 'password': password}
        )
        self.assertEqual(
            self.client_1.get(reverse('blog_create')).status_code, 200
        )
        # Keywords create test
        Keyword.objects.create(title='test_1')
        Keyword.objects.create(title='test_2')
        # Blog create test
        self.client_1.post(reverse('blog_create'),
                           {'title': 'Test note',
                            'content': 'Im testing this content and i </div>like it',
                            'status': 1,
                            'featured_image': '',
                            'keywords_1': 'test_1, test_2, test_3, test_1, test_2',}
                           )
        # Keywords test
        self.assertContains(
            self.client_1.get(reverse('blog_edit', kwargs={'id': 1})), 'value="test_2, test_1"'
        )
        self.assertEqual(
            len(BlogPost.objects.all()[0].keywords.all()), 2
        )
        # Blog edit and html parser test
        self.assertEqual(
            self.client_1.get(reverse('blog_edit', kwargs={'id': 1})).status_code, 200
        )
        self.assertContains(
            self.client_1.get(reverse('blog_edit', kwargs={'id': 1})),
            'Im testing this content and i like it'
        )
        self.client_1.post(reverse('blog_edit', kwargs={'id': 1}),
                           {'title': 'Test note',
                            'content': '<script><b>So slow so tired</div></b></script>',
                            'status': 1,
                            'featured_image': ''})
        self.assertContains(
            self.client_1.get(reverse('blog_edit', kwargs={'id': 1})),
            '<b>So slow so tired</b>'
        )
        self.assertNotContains(
            self.client_1.get(reverse('blog_edit', kwargs={'id': 1})),
            '<script><b>So slow so tired</b></script>'
        )
        # Blog owner test
        self.client_2.post(
            reverse('login'),
            {'username': 'Tester_2', 'password': password}
        )
        self.assertEqual(
            self.client_2.get(reverse('blog_edit', kwargs={'id': 1})).status_code, 302
        )
        # File upload test
        with open('static/media/avatar/default-avatar.jpg', 'r') as img:
            self.client_1.post(reverse('jfu_upload'), {'files[]': img})
        html_img = '<img src=/static/media/uploads/blog/default-avatar.jpg width=300>'
        self.assertContains(
            self.client_1.get(reverse('blog_create')),
            html_img
        )
        # File owner test
        self.assertNotContains(
            self.client_2.get(reverse('blog_create')),
            html_img
        )
        self.client_2.post(reverse('jfu_delete', kwargs={'pk': 1}))
        self.assertContains(
            self.client_1.get(reverse('blog_create')),
            html_img
        )
        # File delete test
        self.client_1.post(reverse('jfu_delete', kwargs={'pk': 1}))
        self.assertNotContains(
            self.client_1.get(reverse('blog_create')),
            html_img
        )
        os.remove('static/media/uploads/blog/default-avatar.jpg')
