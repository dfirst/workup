from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from mezzanine.blog.models import BlogCategory
from mezzanine.generic.models import Keyword

from .models import Topic

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
            self.client_1.get(reverse('topic_create')).status_code, 302
        )
        self.client_1.post(
            reverse('login'),
            {'username': 'Tester_1', 'password': password}
        )
        self.assertEqual(
            self.client_1.get(reverse('topic_create')).status_code, 200
        )
        # Topic create test
        self.client_1.post(reverse('topic_create'),
                           {'title': 'Test note basic',
                            'content': 'Im testing this content and i like it',
                            }
                           )
        # Forum category, keyword filter test
        category = BlogCategory.objects.create(title='Category_Test')
        tag = Keyword.objects.create(title='test_1')
        Keyword.objects.create(title='test_2')
        self.client_1.post(reverse('topic_create'),
                           {'title': 'Test note filter',
                            'content': 'Im testing this content and i like it',
                            'categories': [category.id],
                            'keywords_1': 'test_1, test_2, test_3, test_1, test_2',
                            }
                           )
        # Test Keywords
        topic = Topic.objects.get(title='Test note filter')
        self.assertContains(
            self.client_1.get(reverse('topic_edit', kwargs={'id': topic.id})), 'value="test_2, test_1"'
        )
        self.assertEqual(
            len(topic.keywords.all()), 2
        )
        # Forum category filter test
        self.assertNotContains(
            self.client_1.get(reverse('topic_list_category', kwargs={'category':category.slug})),
            'Test note basic'
        )
        self.assertContains(
            self.client_1.get(reverse('topic_list_category', kwargs={'category':category.slug})),
            'Test note filter'
        )
        # Forum tags filter test
        self.assertNotContains(
            self.client_1.get(reverse('topic_list_tag', kwargs={'tag': tag.slug})),
            'Test note basics'
        )
        self.assertContains(
            self.client_1.get(reverse('topic_list_tag', kwargs={'tag': tag.slug})),
            'Test note filter'
        )
        # Forum main page test
        self.assertContains(
            self.client_1.get(reverse('topic_list_latest')),
            'Test note basic'
        )
        # Topic detail test
        topic = Topic.objects.get(pk=1)
        self.assertEqual(
            self.client_1.get(reverse('topic_detail', kwargs={'slug': topic.slug})).status_code, 200
        )
        # Topic edit and html parser test
        self.assertEqual(
            self.client_1.get(reverse('topic_edit', kwargs={'id': 1})).status_code, 200
        )
        self.assertContains(
            self.client_1.get(reverse('topic_edit', kwargs={'id': 1})),
            'Im testing this content and i like it'
        )
        self.client_1.post(reverse('topic_edit', kwargs={'id': 1}),
                           {'title': 'Test note',
                            'content': '<script><b>So slow so tired</b></script>',})
        self.assertContains(
            self.client_1.get(reverse('topic_edit', kwargs={'id': 1})),
            '<b>So slow so tired</b>'
        )
        self.assertNotContains(
            self.client_1.get(reverse('topic_edit', kwargs={'id': 1})),
            '<script>So slow so tired</script>'
        )
        # Topic owner test
        self.client_2.post(
            reverse('login'),
            {'username': 'Tester_2', 'password': password}
        )
        self.assertEqual(
            self.client_2.get(reverse('topic_edit', kwargs={'id': 1})).status_code, 302
        )
