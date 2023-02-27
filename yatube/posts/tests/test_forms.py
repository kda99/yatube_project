import shutil
import tempfile
from http import HTTPStatus

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from posts.models import Group, Post, User

POST_CREATE = reverse('posts:post_create')
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='test_title',
            description='test_description',
            slug='test-slug'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='test_post',
            author=cls.author,
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='User')
        self.anonim_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_post_anonim(self):
        """аноним не может создать пост"""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }

        response = self.anonim_client.post(
            POST_CREATE,
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }

        response = self.authorized_client.post(
            POST_CREATE,
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        last_post = Post.objects.order_by('-id')[0]

        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.author, self.author)

    def test_edit_post_anonim(self):
        """аноним не может отредактировать пост"""
        posts_count = Post.objects.count()
        POST_EDIT = reverse('posts:post_edit', args=({self.post.id}))
        form_data = {
            'text': 'Отредактированный текст',
            'group': self.group.id,
        }

        self.anonim_client.post(
            POST_EDIT,
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(not Post.objects.filter(
            text='Отредактированный текст').count())

    def test_edit_post(self):
        """Валидная форма редактирует пост"""
        posts_count = Post.objects.count()
        POST_EDIT = reverse('posts:post_edit', args=({self.post.id}))
        form_data = {
            'text': 'Отредактированный текст',
            'group': self.group.id,
        }

        response = self.authorized_client.post(
            POST_EDIT,
            data=form_data,
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            "posts:post_detail", kwargs={"post_id": self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(
            text='Отредактированный текст').count())

        last_post = Post.objects.order_by('-id')[0]

        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.author, self.author)

    def test_image_context(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Отредактированный текст',
            'group': self.group.id,
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:index'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
