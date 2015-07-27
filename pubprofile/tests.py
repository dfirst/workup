# -*- coding: utf-8 -*-
from future.utils import native_str

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from mezzanine.blog.models import BlogPost
from mezzanine.generic.forms import RatingForm
from mezzanine.generic.models import ThreadedComment
from mezzanine.conf import settings

from workup.forum.models import Topic

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

    def test_comments_extension(self):
        # Create objects
        blog_post = BlogPost.objects.create(title='Post', user=self.user)
        # Auth clients
        self.client_1.post(
            reverse('login'),
            {'username': 'Tester_1', 'password': password}
        )
        self.client_2.post(
            reverse('login'),
            {'username': 'Tester_2', 'password': password}
        )
        # Test rating system
        data = RatingForm(None, blog_post).initial
        rating_list = [-1,-1,1,1,1]
        for value in rating_list:
            data["value"] = value
            # Simulate voting by object author and user
            response_1 = self.client_1.post(reverse("rating"), data=data)
            response_2 = self.client_2.post(reverse("rating"), data=data)
            # Django doesn't seem to support unicode cookie keys correctly on
            # Python 2. See https://code.djangoproject.com/ticket/19802
            response_1.delete_cookie(native_str("mezzanine-rating"))
            response_2.delete_cookie(native_str("mezzanine-rating"))
        blog_post = BlogPost.objects.get(id=1)
        # Test karma
        self.assertEqual(self.user.userprofile.karma, sum(rating_list))
        # Test rating for object
        self.assertEqual(blog_post.rating_sum, sum(rating_list)*2)
        # Test account blogpost
        BlogPost.objects.create(title='Published object', user=self.user)
        BlogPost.objects.create(title='Draft object', user=self.user, status=1)
        # Test account blogpost owner
        response = self.client_1.get(reverse('blog_list_user', kwargs={'username': self.user}))
        self.assertContains(response, 'Published object')
        self.assertContains(response, 'Draft object')
        # Test account blogpost user
        response = self.client_2.get(reverse('blog_list_user', kwargs={'username': self.user}))
        self.assertContains(response, 'Published object')
        self.assertNotContains(response, 'Draft object')
        # Test account forum
        Topic.objects.create(title='Published object', user=self.user)
        response = self.client_1.get(reverse('topic_list_user', kwargs={'username': self.user}))
        # Test account forum owner
        self.assertContains(response, 'Published object')
        self.assertContains(response, 'Правка')
        # Test account forum user
        response = self.client_2.get(reverse('topic_list_user', kwargs={'username': self.user}))
        self.assertContains(response, 'Published object')
        self.assertNotContains(response, 'Правка')
        # Test account comments
        blog_post = BlogPost.objects.create(title='Post', user=self.user)
        content_type = ContentType.objects.get_for_model(blog_post)
        kwargs = {
            'content_type': content_type,
            'object_pk': blog_post.id,
            'site_id': settings.SITE_ID,
            'comment': 'Test comment for me',
            'user': self.user,
                  }
        ThreadedComment.objects.create(**kwargs)
        # Test account comments owner
        response = self.client_1.get(reverse('comment_list_user', kwargs={'username': self.user}))
        self.assertContains(response, 'Test comment for me')
        self.assertContains(response, 'Правка')
        # Test account comments user
        response = self.client_2.get(reverse('comment_list_user', kwargs={'username': self.user}))
        self.assertContains(response, 'Test comment for me')
        self.assertNotContains(response, 'Правка')
        # Test profile url
        self.assertEqual(
            self.client_1.get(reverse('profile', kwargs={'username': self.user})).status_code, 200
        )