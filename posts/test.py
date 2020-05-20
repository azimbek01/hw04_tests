from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import Post, Group


def get_post_context(post, context):
    for value in context['page']:
        if post.id == value.id:
            return value
    return


class test_profile_after_registration(TestCase):
    def setUp(self):
        self.user = get_user_model()(username='new_user')
        self.user.save()
        self.client.force_login(self.user)

    def test_get_profile(self):
        url_profile = reverse(
            'profile', kwargs={'username': self.user.username})
        response = self.client.get(url_profile)
        self.assertEqual(response.status_code, 200)


class test_authorized_user_new_post(TestCase):
    def setUp(self):
        self.user = get_user_model()(username='new_user')
        self.user.save()
        self.client.force_login(self.user)

    def test_new_post(self):
        url_new_post = reverse('new_post')
        data = {
            'text': 'Проверка нового поста!',
            'author': self.user,
            'group_posts': 1
        }
        self.assertEquals(Post.objects.all().count(), 0)

        response = self.client.post(url_new_post, data, follow=True)
        self.assertEquals(response.status_code, 200)
        post = Post.objects.filter(author=self.user,
                                   text=data['text']).first()
        self.assertNotEqual(post, None)


class test_not_authorized_user_new_post(TestCase):
    def setUp(self):
        self.user = get_user_model()(username='new_user')
        self.user.save()

    def test_get_new_post(self):
        url_new_post = reverse('new_post')

        response = self.client.get(url_new_post)
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, '/auth/login/?next=/new/')


class test_post_view(TestCase):
    def setUp(self):
        self.user = get_user_model()(username='new_user')
        self.user.save()
        self.client.force_login(self.user)

    def test_view_post(self):
        url_new_post = reverse('new_post')
        data = {
            'text': 'Пост для тестирования просмотра',
            'author': self.user,
            'group_posts': 1
        }

        response_new_post = self.client.post(url_new_post, data, follow=True)
        post = Post.objects.filter(author=self.user,
                                   text=data['text']).first()
        post_context = get_post_context(post, response_new_post.context)
        self.assertNotEquals(
            post_context, None,
            msg='Новая запись не появилась на главной странице сайта')

        url_profile = reverse(
                     'profile', kwargs={'username': self.user.username})

        response_profile = self.client.get(url_profile)
        post_context = get_post_context(post, response_profile.context)
        self.assertNotEquals(
            post_context, None,
            msg='Новая запись не появилась на странице пользователя')

        url_post = reverse(
            'post', kwargs={'username': self.user.username,
                            'post_id': post.id})

        response_post = self.client.get(url_post)
        self.assertEquals(
            response_post.context['post'].id, post.id,
            msg='Новая запись не появилась на странице просмотра поста')


class test_post_edit(TestCase):
    def setUp(self):
        self.user = get_user_model()(username='new_user')
        self.user.save()
        self.client.force_login(self.user)

        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test',
            description='Тест'
        )

        self.post = Post.objects.create(
                        text='Тестовый пост до изменения',
                        author=self.user,
                        group=self.group)

    def test_post_edit(self):
        data = {
            'text': 'Тестовый пост после изменения',
            'author': self.user,
            'group': self.group.id
        }
        post = Post.objects.filter(author=self.user,
                                   group=self.group).first()
        self.assertNotEqual(post, None)

        url_post_edit = reverse(
            'post_edit', kwargs={'username': self.user.username,
                                 'post_id': post.id})

        response_edit = self.client.post(url_post_edit, data, follow=True)

        self.assertEquals(
            response_edit.context['post'].text, data['text'],
            msg='Содержимое поста не изменилось на странице просмотра поста')

        url_profile = reverse(
            'profile', kwargs={'username': self.user.username})

        response_profile = self.client.get(url_profile)
        post_context = get_post_context(post, response_profile.context)

        self.assertNotEquals(post_context, None)
        self.assertEquals(
            post_context.text, data['text'],
            'Содержимое поста не изменилось на странице пользователя')

        response_index = self.client.get('/')
        post_context = get_post_context(post, response_index.context)

        self.assertNotEquals(post_context, None)
        self.assertEquals(
            post_context.text, data['text'],
            'Содержимое поста не изменилось на главной странице')
