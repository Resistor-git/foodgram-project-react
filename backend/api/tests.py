# from http import HTTPStatus
# from typing import Dict
#
# from django.template.response import TemplateResponse
# from django.contrib.auth import get_user_model
# from django.test import TestCase, Client
# from django.urls import reverse
# from django.core.cache import cache
#
# from ..recipes.models import Recipe
#
# User = get_user_model()
#
#
# class StaticURLTests(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         """Creates test post, group and users.
#         Post author is post_author_user.
#         Only post_author_user can edit post, so he gets '200' in response to
#         /posts/{StaticURLTests.post.id}/edit/
#         Other users should be redirected (302)"""
#         super().setUpClass()
#         # cls.guest_user: User = User.objects.create_user(
#         #     username='test_guest_user'
#         # )
#         cls.authorized_user: User = User.objects.create_user(
#             username='authorized_user'
#         )
#         cls.post_author_user: User = User.objects.create_user(
#             username='recipe_author_user'
#         )
#         cls.post: Recipe = Recipe.objects.create(
#             text='Тестовый пост',
#             author=cls.recipe_author_user,
#         )
#         cls.group: Group = Group.objects.create(
#             title='Тестовая группа',
#             slug='test_slug',
#             description='Тестовое описание',
#         )
#
#     # def setUp(self):
#     #     """Create guest client and 2 authorised clients"""
#     #     self.guest_client: Client = Client()
#     #     self.authorized_client: Client = Client()
#     #     self.post_author_client: Client = Client()
#     #     self.authorized_client.force_login(StaticURLTests.authorized_user)
#     #     self.post_author_client.force_login(StaticURLTests.post_author_user)
#     #     cache.clear()
#
#     def test_url_codes_guest_user(self):
#         """ПЕРЕПИСАТЬ Should not allow to: create or edit post, comment, follow (302)"""
#         url_codes: Dict[str, HTTPStatus] = {
#             '': HTTPStatus.OK,
#             # f'/group/{StaticURLTests.group.slug}/': HTTPStatus.OK,
#             # (f'/profile/'
#             #  f'{StaticURLTests.post_author_user.username}/'): HTTPStatus.OK,
#             # f'/posts/{StaticURLTests.post.id}/': HTTPStatus.OK,
#             # '/create/': HTTPStatus.FOUND,
#             # f'/posts/{StaticURLTests.post.id}/edit/': HTTPStatus.FOUND,
#             # f'/posts/{StaticURLTests.post.id}/comment/': HTTPStatus.FOUND,
#             # '/follow/': HTTPStatus.FOUND,
#             # (f'/profile/{StaticURLTests.post_author_user.username}'
#             #  '/follow/'): HTTPStatus.FOUND,
#             # (f'/profile/{StaticURLTests.post_author_user.username}'
#             #  '/unfollow/'): HTTPStatus.FOUND,
#             # '/unexisting_page/': HTTPStatus.NOT_FOUND,
#         }
#         for url, code in url_codes.items():
#             with self.subTest(url=url):
#                 response_code = self.client.get(url).status_code
#                 self.assertEqual(response_code, code)
