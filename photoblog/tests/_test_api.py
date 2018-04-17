# # pylint: disable=no-member
# import json
# import base64
# import os
# from django.conf import settings
# from django.contrib.auth.models import Group
# from django.core.exceptions import ValidationError
# from django.urls import reverse
# from django.test import override_settings
# from rest_framework import status
# from rest_framework.test import APITestCase, APIClient, APIRequestFactory

# from django.core.files.uploadedfile import SimpleUploadedFile

# from django.core.management import call_command

# from accounts.models import User

# from gallery.models import (
#     Category,
#     Collection,
#     Dimension,
#     Entry,
#     Image,
#     Story,
# )



# TEST_MEDIA_ROOT = "/tmp/django_test_media_dump"

# def authed_client(client, user):
#     """Authenticates the client with the auth api."""
#     url = reverse('accounts:get-token')
#     res = client.post(url, data={
#         'email': user['email'],
#         'password': user['password']
#     })
#     client.credentials(HTTP_AUTHORIZATION=f'Token {res.data["token"]}')
#     return client


# class DimensionAPITests(APITestCase):
#     @classmethod
#     def setUpTestData(cls):
#         user_one = User.objects.create_user(email='johnny@theswamp.com',
#                                             username='johnnythegodling',
#                                             password='testpassword')
#         user_one.save()
#         cls.user1 = {
#             'obj': user_one,
#             'email': 'johnny@theswamp.com',
#             'username': 'johnnythegodling',
#             'password': 'testpassword'
#         }
#         cls.authed_client = authed_client(APIClient(), cls.user1)


#     def test_anon_cannot_create(self):
#         url = reverse('dimension-list')
#         response = self.client.post(url, data={
#             'unit': 'in',
#             'height': 10,
#             'length': 10,
#         })
#         self.assertEqual(response.status_code, 401)
#         self.assertIn('Authentication credentials were not provided', 
#                       response.data['detail'])

#     def test_user_can_create(self):
#         url = reverse('dimension-list')
#         response = self.authed_client.post(url, data={
#             'unit': 'in',
#             'height': 10,
#             'length': 12,
#         })
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(float(10), response.data['height'])

#     def test_user_can_delete(self):
#         dimension = Dimension.objects.create(created_by=self.user1['obj'],
#                                              unit='ft', height=3, length=5,
#                                              width=1)
#         url = reverse('dimension-detail', kwargs={'pk': dimension.id})
#         response = self.authed_client.delete(url)
#         self.assertEqual(response.status_code, 204)
#         self.assertNotIn(dimension, Dimension.objects.all())

#     def test_user_can_edit(self):
#         dimension = Dimension.objects.create(created_by=self.user1['obj'],
#                                              unit='ft', height=3, length=5,
#                                              width=1)
#         url = reverse('dimension-detail', kwargs={'pk': dimension.id})
#         response = self.authed_client.patch(url, data={
#             'width': 6,
#         })
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data['width'], 6)


# class CategoryAPITests(APITestCase):

#     @classmethod
#     def setUpTestData(cls):
#         user_one = User.objects.create_user(email='johnny@theswamp.com',
#                                             username='johnnythegodling',
#                                             password='testpassword')
#         user_one.save()
#         cls.user1 = {
#             'obj': user_one,
#             'email': 'johnny@theswamp.com',
#             'username': 'johnnythegodling',
#             'password': 'testpassword'
#         }
#         cls.authed_client = authed_client(APIClient(), cls.user1)

#     def test_anon_cannot_create(self):
#         url = reverse('category-list')
#         response = self.client.post(url, data={
#             'name_en': 'Anon attempts a category!',
#             'description': 'And it is anonymous'
#         })
#         self.assertEqual(response.status_code, 401)
#         self.assertIn('Authentication credentials were not provided', 
#                       response.data['detail'])

#     def test_user_can_create(self):
#         url = reverse('category-list')
#         response = self.authed_client.post(url, data={
#             'name': 'I created a category!',
#             'description': 'And it is not anonymous'
#         })
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual('I created a category!', response.data['name'])

#     def test_user_can_delete(self):
#         category = Category.objects.create(name='Test category',
#                                            description='best category',
#                                            created_by=self.user1['obj'])
#         url = reverse('category-detail', kwargs={'slug': category.slug})
#         response = self.authed_client.delete(url)
#         self.assertEqual(response.status_code, 204)
#         self.assertNotIn(category, Category.objects.all())

#     def test_user_can_edit(self):
#         category = Category.objects.create(name='Test category',
#                                            description='best category',
#                                            created_by=self.user1['obj'])
#         url = reverse('category-detail', kwargs={'slug': category.slug})
#         response = self.authed_client.patch(url, data={
#             'name': 'New name!',
#             'description': 'new description too!',
#         })
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data['name'], 'New name!')

#     def test_get_entries_GET(self):
#         category = Category.objects.create(name='Test category',
#                                            description='best category',
#                                            created_by=self.user1['obj'])
#         Entry.objects.create(title='Categorized entry!',
#                                      description='Fun!',
#                                      category=category,
#                                      created_by=self.user1['obj'])
#         url = reverse('category-entries', kwargs={'slug': category.slug})
#         response = self.authed_client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('Categorized entry!', response.data['results'][0]['title_en'])

#     def test_get_stories_GET(self):
#         category = Category.objects.create(name='Test category',
#                                            description='best category',
#                                            created_by=self.user1['obj'])
#         Story.objects.create(title='Categorized story',
#                                      description='Fun!',
#                                      text='Fun indeed',
#                                      category=category,
#                                      created_by=self.user1['obj'])
#         url = reverse('category-stories', kwargs={'slug': category.slug})
#         response = self.authed_client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('Categorized story', response.data['results'][0]['title_en'])

#     def test_get_collections_GET(self):
#         category = Category.objects.create(name='Test category',
#                                            description='best category',
#                                            created_by=self.user1['obj'])
#         Collection.objects.create(title='Categorized collection',
#                                      description='Fun!',
#                                      category=category,
#                                      created_by=self.user1['obj'])
#         url = reverse('category-collections', kwargs={'slug': category.slug})
#         response = self.authed_client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('Categorized collection', response.data['results'][0]['title_en'])


# @override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
# class EntryAPITests(APITestCase):

#     @classmethod
#     def setUpTestData(cls):
#         user_one = User.objects.create_user(email='johnny@theswamp.com',
#                                             username='johnnythegodling',
#                                             password='testpassword')
#         user_one.save()
#         user_two = User.objects.create_user(email='agatha@theswamp.com',
#                                             username='agathathehuman',
#                                             password='testpassword')
#         user_two.save(),
#         cls.user1 = {
#             'user': user_one,
#             'email': 'johnny@theswamp.com',
#             'username': 'johnnythegodling',
#             'password': 'testpassword'
#         }
#         cls.user2 = {
#             'user': user_two,
#             'email': 'agatha@theswamp.com',
#             'username': 'agathathehuman',
#             'password': 'testpassword'
#         }


#     def test_anon_cannot_create(self):
#         url = reverse('entry-list')
#         response = self.client.post(url, data={
#             'title': 'AnonPost!',
#             'description': 'is anonymous'
#         })
#         self.assertEqual(response.status_code, 401)
#         self.assertIn('Authentication credentials were not provided', response.data['detail'])

#     def test_user_can_create_entry(self):
#         url = reverse('entry-list')
#         client = authed_client(APIClient(), self.user1)
#         response = client.post(url, data={
#                 'title': 'My brand new post!',
#                 'description': 'Brand new indeed!'
#             },
#         )
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(response.data['created_by'], self.user1['username'])
    
#     def test_user_cannot_create_duplicate_entry(self):
#         url = reverse('entry-list')
#         client = authed_client(APIClient(), self.user1)
#         response1 = client.post(url, data={
#                 'title': 'A singular, unique post',
#                 'description': 'With a singular, unique description'
#             },
#         )
#         with self.assertRaises(ValidationError):
#             response2 = client.post(url, data={
#                     'title': 'A singular, unique post',
#                     'description': 'With a not so singular, unique description'
#                 })
#         # self.assertEqual(
#         #     response2.data['error'],
#         #     'You already have an Entry with this title'
#         # )
    
#     def test_user_can_edit_entry(self):
#         post_url = reverse('entry-list')
#         client = authed_client(APIClient(), self.user1)
#         post_response = client.post(post_url, data={
#             'title': 'First updatable entry',
#             'description': 'Title to be updated'
#         })
#         id_ = post_response.data['id']
#         put_url = reverse('entry-detail', args=(id_,))
#         response = client.put(put_url, data={
#             'title': 'Different title',
#             'description': 'Different description'
#         })
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(
#             response.data['description'],
#             'Different description'
#         )
    
#     def test_user_can_delete_entry(self):
#         post_url = reverse('entry-list')
#         client = authed_client(APIClient(), self.user1)
#         post_response = client.post(post_url, data={
#             'title': 'First updatable entry',
#             'description': 'Title to be updated'
#         })
#         id_ = post_response.data['id']
#         delete_url = reverse('entry-detail', args=(id_,))
#         response = client.delete(delete_url)
#         self.assertEqual(response.status_code, 204)

#     def test_user_cannot_edit_other_user_entry(self):
#         post_url = reverse('entry-list')
#         post_client = authed_client(APIClient(), self.user1)
#         post_response = post_client.post(post_url, data={
#             'title': "This is Johnny's entry",
#             'description': "This is Johnny's description"
#         })
#         id_ = post_response.data['id']
#         put_client = authed_client(APIClient(), self.user2)
#         put_url = reverse('entry-detail', args=(id_,))
#         response = put_client.put(put_url, data={
#             'title': 'Agatha is writing now',
#             'description': 'Because my description is better'
#         })
#         self.assertEqual(response.status_code, 404)
#         self.assertEqual(
#             response.data['detail'],
#             "You do not have permission to perform this action."
#         )

#     def test_user_cannot_delete_other_user_entry(self):
#         post_url = reverse('entry-list')
#         post_client = authed_client(APIClient(), self.user1)
#         post_response = post_client.post(post_url, data={
#             'title': "This is Johnny's entry",
#             'description': "This is Johnny's description"
#         })
#         id_ = post_response.data['id']
#         put_client = authed_client(APIClient(), self.user2)
#         delete_url = reverse('entry-detail', args=(id_,))
#         response = put_client.delete(delete_url)
#         self.assertEqual(response.status_code, 404)
#         self.assertEqual(
#             response.data['detail'],
#             "You do not have permission to perform this action."
#         )

#     def test_user_can_view_other_user_entry(self):
#         post_url = reverse('entry-list')
#         post_client = authed_client(APIClient(), self.user1)
#         post_response = post_client.post(post_url, data={
#             'title': "Entry by Johnny",
#             'description': "Hello Agatha!"
#         })
#         id_ = post_response.data['id']
#         client = authed_client(APIClient(), self.user2)
#         get_url = reverse('entry-detail', args=(id_,))
#         response = client.get(get_url)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data['title'], "Entry by Johnny")

#     def test_anon_user_can_view_other_user_entry(self):
#         post_url = reverse('entry-list')
#         client = authed_client(APIClient(), self.user2)
#         post_response = client.post(post_url, data={
#             'title': "Entry by Johnny",
#             'description': "Hello Agatha!"
#         })
#         id_ = post_response.data['id']
#         anon_client = APIClient()
#         get_url = reverse('entry-detail', args=(id_,))
#         response = anon_client.get(get_url)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data['title'], "Entry by Johnny")


# class BaseAPITests(APITestCase):
#     """Tests gallery.api.BaseViewSet functionality using an Entry
#     instance, particularly Image setting methods."""

#     @classmethod
#     def setUpTestData(cls):
#         call_command('create_groups')
#         user_one = User.objects.create_user(email='johnny@theswamp.com',
#                                             username='johnnythegodling',
#                                             password='testpassword')
#         STAFF = Group.objects.get(name='Superusers')
#         user_one.groups.add(STAFF)
#         user_one.save()
#         cls.user1 = {
#             'obj': user_one,
#             'email': 'johnny@theswamp.com',
#             'username': 'johnnythegodling',
#             'password': 'testpassword'
#         }
#         cls.authed_client = authed_client(APIClient(), cls.user1)
#         cls.path1 = os.path.join(
#             settings.BASE_DIR, 'gallery/static/gallery/img/diy.jpg')
#         cls.file1 = SimpleUploadedFile(
#             name='diy.jpg',
#             content=open(cls.path1, 'rb').read(),
#             content_type='image/jpeg',
#         )
#         cls.path2 = os.path.join(
#             settings.BASE_DIR, 'gallery/static/gallery/img/temple.jpg')
#         cls.file2 = SimpleUploadedFile(
#             name='temple.jpg',
#             content=open(cls.path2, 'rb').read(),
#             content_type='image/jpeg',
#         )
#         cls.path3 = os.path.join(
#             settings.BASE_DIR, 'gallery/static/gallery/img/lakeside.jpg')
#         cls.file3 = SimpleUploadedFile(
#             name='lakeside.jpg',
#             content=open(cls.path3, 'rb').read(),
#             content_type='image/jpeg',
#         )

#     def test_add_images_works(self):
#         entry_res = self.authed_client.post(reverse('entry-list'), data={
#             'title': 'test-entry',
#             'description': 'it exists', 
#         })
#         entry = entry_res.data
#         data = [
#             {
#                 'title_en': 'image1',
#                 'image': base64.b64encode(b''.join(self.file1.file.readlines()))
#             },
#             {
#                 'title_en': 'image2',
#                 'image': base64.b64encode(b''.join(self.file2.file.readlines()))
#             },
#             {
#                 'title_en': 'image3',
#                 'image': base64.b64encode(b''.join(self.file3.file.readlines()))
#             }
#         ]
#         # import pdb; pdb.set_trace()
#         url = reverse('entry-add-images', kwargs={'pk': entry['id']})
#         response = self.authed_client.post(url, data=data, format='json')
#         self.assertEqual(response.status_code, 200)


# class ImageAPITests(APITestCase):

#     @classmethod
#     def setUpTestData(cls):
#         user_one = User.objects.create_user(
#                             email='johnny@theswamp.com',
#                             username='johnnythegodling',
#                             password='testpassword'
#                         )
#         user_one.save()
#         user_two = User.objects.create_user(
#                             email='agatha@theswamp.com',
#                             username='agathathehuman',
#                             password='testpassword'
#                         )
#         user_two.save(),
#         cls.user1 = {
#             'user': user_one,
#             'email': 'johnny@theswamp.com',
#             'username': 'johnnythegodling',
#             'password': 'testpassword'
#         }
#         cls.user2 = {
#             'user': user_two,
#             'email': 'agatha@theswamp.com',
#             'username': 'agathathehuman',
#             'password': 'testpassword'
#         }
#         cls.image_path = os.path.join(
#             settings.BASE_DIR, 'gallery/static/gallery/img/diy.jpg')
#         cls.test_image = SimpleUploadedFile(
#             name='a_cover_tale.jpg',
#             content=open(cls.image_path, 'rb').read(),
#             content_type='image/jpeg',
#         )

#     def test_cannot_create_entry_image_as_anon_user(self):
#         entry_url = reverse('entry-list')
#         url = reverse('image-list')
#         client = authed_client(APIClient(), self.user1)
#         entry_res = client.post(entry_url, data={
#             'title': 'Anon makes an entry',
#             'description': 'And a not so verbose description',
#         })
#         client = APIClient()
#         response = client.post(url, data={
#                 'title': 'Anon posts an image!',
#                 'caption': 'Brand new indeed!',
#                 'entry': entry_res.data['id'],
#                 'image': SimpleUploadedFile(
#                         name='a_cover_tale.jpg',
#                         content=open(self.image_path, 'rb').read(),
#                         content_type='image/jpeg')
#             },
#         )
#         self.assertEqual(response.status_code, 401)
#         self.assertIn('Authentication credentials were not provided', response.data['detail'])


#     def test_user_can_create_entry_image(self):
#         entry_url = reverse('entry-list')
#         url = reverse('image-list')
#         client = authed_client(APIClient(), self.user1)
#         entry_res = client.post(entry_url, data={
#             'title': 'Good ole Johnny makes an entry',
#             'description': 'And a quite verbose description',
#         })
#         response = client.post(url, data={
#                 'title': 'New image for Johnnysdf',
#                 'caption': 'Brand new indeed!',
#                 'entry': entry_res.data['id'],
#                 'image': SimpleUploadedFile(
#                         name='a_cover_tale.jpg',
#                         content=open(self.image_path, 'rb').read(),
#                         content_type='image/jpeg')
#             },
#         )
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(response.data['user'], self.user1['username'])
    
#     def test_user_cannot_create_duplicate_title_images_for_same_entry(self):
#         entry_url = reverse('entry-list')
#         url = reverse('image-list')
#         client = authed_client(APIClient(), self.user1)
#         entry_res = client.post(entry_url, data={
#             'title': 'Johnny will now test duplicate-title images',
#             'description': 'Why do I even need this description?',
#         })
#         response1 = client.post(url, data={
#                 'title': 'A singular, unique image',
#                 'description': 'With a singular, unique description',
#                 'entry': entry_res.data['id'],
#                 'image': SimpleUploadedFile(
#                         name='a_cover_tale.jpg',
#                         content=open(self.image_path, 'rb').read(),
#                         content_type='image/jpeg')
#             },
#         )
#         response2 = client.post(url, data={
#                 'title': 'A singular, unique image',
#                 'description': 'With a not so singular, unique description',
#                 'entry': entry_res.data['id'],
#                 'image': SimpleUploadedFile(
#                         name='a_cover_tale.jpg',
#                         content=open(self.image_path, 'rb').read(),
#                         content_type='image/jpeg')
#             },
#         )
#         self.assertEqual(response2.status_code, 400)
#         self.assertEqual(
#             response2.data['non_field_errors'],
#             ['The fields entry, title must make a unique set.']
#         )
    
#     # def test_user_can_edit_entry(self):
#     #     post_url = reverse('entry-list')
#     #     self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1}')
#     #     post_response = self.client.post(post_url, data={
#     #         'title': 'First updatable entry',
#     #         'description': 'Title to be updated'
#     #     })
#     #     id_ = post_response.data['id']
#     #     put_url = reverse('entry-detail', args=(id_,))
#     #     response = self.client.put(put_url, data={
#     #         'title': 'Different title',
#     #         'description': 'Different description'
#     #     })
#     #     self.assertEqual(response.status_code, 200)
#     #     self.assertEqual(
#     #         response.data['description'],
#     #         'Different description'
#     #     )
    
#     # def test_user_can_delete_entry(self):
#     #     post_url = reverse('entry-list')
#     #     self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1}')
#     #     post_response = self.client.post(post_url, data={
#     #         'title': 'First updatable entry',
#     #         'description': 'Title to be updated'
#     #     })
#     #     id_ = post_response.data['id']
#     #     delete_url = reverse('entry-detail', args=(id_,))
#     #     response = self.client.delete(delete_url)
#     #     self.assertEqual(response.status_code, 204)

#     # def test_user_cannot_edit_other_user_entry(self):
#     #     post_url = reverse('entry-list')
#     #     self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1}')
#     #     post_response = self.client.post(post_url, data={
#     #         'title': "This is Johnny's entry",
#     #         'description': "This is Johnny's description"
#     #     })
#     #     id_ = post_response.data['id']
#     #     self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token2}')
#     #     put_url = reverse('entry-detail', args=(id_,))
#     #     response = self.client.put(put_url, data={
#     #         'title': 'Agatha is writing now',
#     #         'description': 'Because my description is better'
#     #     })
#     #     self.assertEqual(response.status_code, 403)
#     #     self.assertEqual(
#     #         response.data['detail'],
#     #         "You do not have permission to perform this action."
#     #     )

#     # def test_user_cannot_delete_other_user_entry(self):
#     #     post_url = reverse('entry-list')
#     #     self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1}')
#     #     post_response = self.client.post(post_url, data={
#     #         'title': "This is Johnny's entry",
#     #         'description': "This is Johnny's description"
#     #     })
#     #     id_ = post_response.data['id']
#     #     self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token2}')
#     #     delete_url = reverse('entry-detail', args=(id_,))
#     #     response = self.client.delete(delete_url)
#     #     self.assertEqual(response.status_code, 403)
#     #     self.assertEqual(
#     #         response.data['detail'],
#     #         "You do not have permission to perform this action."
#     #     )

#     # def test_user_can_view_other_user_entry(self):
#     #     post_url = reverse('entry-list')
#     #     self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1}')
#     #     post_response = self.client.post(post_url, data={
#     #         'title': "Entry by Johnny",
#     #         'description': "Hello Agatha!"
#     #     })
#     #     id_ = post_response.data['id']
#     #     self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token2}')
#     #     get_url = reverse('entry-detail', args=(id_,))
#     #     response = self.client.get(get_url)
#     #     self.assertEqual(response.status_code, 200)
#     #     self.assertEqual(response.data['title'], "Entry by Johnny")

#     # def test_anon_user_can_view_other_user_entry(self):
#     #     post_url = reverse('entry-list')
#     #     self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1}')
#     #     post_response = self.client.post(post_url, data={
#     #         'title': "Entry by Johnny",
#     #         'description': "Hello Agatha!"
#     #     })
#     #     id_ = post_response.data['id']
#     #     self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token2}')
#     #     get_url = reverse('entry-detail', args=(id_,))
#     #     response = self.client.get(get_url)
#     #     self.assertEqual(response.status_code, 200)
#     #     self.assertEqual(response.data['title'], "Entry by Johnny")


# # class ThrottleTests(APITestCase):
# #     TESTING_THRESHOLD = '5/min'

# #     @override_settings(THROTTLE_THESHOLD=TESTING_THRESHOLD)
# #     def test-