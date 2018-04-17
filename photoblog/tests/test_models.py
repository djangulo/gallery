# pylint: disable=no-member, missing-docstring, invalid-name, too-many-lines
# pylint: disable=too-many-public-methods
"""Unit tests for photoblog models."""
import os
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from photoblog.models import (
    Category,
    Collection,
    Dimension,
    Entry,
    Image,
    Story,
)
from accounts.models import User

IMAGE_PATH = os.path.join(
    settings.BASE_DIR, 'photoblog/static/photoblog/img/diy.jpg')

TEST_MEDIA_ROOT = "/tmp/django_test_media_dump"

class DimensionModelTests(TestCase):
    """Unit tests for Dimension model."""

    def test_can_create_dimension(self):
        twelve_by_twelve = Dimension.objects.create(height=12, length=12,
                                                    unit='ft')
        self.assertEqual(twelve_by_twelve, Dimension.objects.first())

    def test_can_change_units(self):
        two_by_four = Dimension.objects.create(height=0.5, length=3,
                                               width=0.2, unit='ft')

        two_by_four.convert_unit('in')
        self.assertEqual(two_by_four.unit, 'in')
        self.assertEqual(two_by_four.length, 36)

    def test_display_as_unit_doesnt_change_unit(self):
        two_by_four = Dimension.objects.create(height=4, length=36, width=2,
                                               unit='in')
        two_by_four.display_as_unit('ft')
        self.assertEqual(two_by_four.unit, 'in')


class CategoryModelTests(TestCase):
    """Unit tests for Category model."""
    @classmethod
    def setUpTestData(cls):
        user_one = User.objects.create_user(email='test.user@example.com',
                                            username='test_user223',
                                            password='testpassword')
        user_one.save()
        cls.user1 = {
            'obj': user_one,
            'email': 'test.user@example.com',
            'username': 'test_user223',
            'password': 'testpassword'
        }

    def test_anon_cannot_create_category(self):
        oil = Category(name='Oil paintings',
                                      description='Oil paintings are hard')
        with self.assertRaises(ValidationError):
            oil.save()

    def test_user_can_create_category(self):
        oil = Category.objects.create(name='Oil paintings',
                                      description='Oil paintings are hard',
                                      created_by=self.user1['obj'])
        self.assertEqual(oil, Category.objects.first())

    def test_slug_is_populated_properly(self):
        oil = Category.objects.create(name='Oil paintings',
                                      description='Oil paintings are hard',
                                      created_by=self.user1['obj'])
        self.assertEqual(oil.slug, 'oil-paintings')

    def test_reverse_entry_relation_accessor(self):
        category = Category.objects.create(name='Test category',
                                           description='Best category!',
                                           created_by=self.user1['obj'])
        entry = Entry.objects.create(title='Existential dread',
                                     slug='existential-dread',
                                     description="Don't let it set in",
                                     category=category,
                                     created_by=self.user1['obj'])
        self.assertIn(entry, category.photoblog_entry_set.all())

    def test_reverse_entry_query_accessor(self):
        category = Category.objects.create(name='Test category',
                                           description='Best category!',
                                           created_by=self.user1['obj'])
        entry = Entry.objects.create(title='Existential dread',
                                     slug='existential-dread',
                                     description="Don't let it set in",
                                     category=category,
                                     created_by=self.user1['obj'])
        self.assertEqual(category,
                         Category.objects.get(
                             photoblog_entry__title=entry.title))

    def test_reverse_collection_relation_accessor(self):
        category = Category.objects.create(name='Test category',
                                           description='Best category!',
                                           created_by=self.user1['obj'])
        collection = Collection.objects.create(
            title='A bunch of things',
            description="Together in a collection",
            category=category,
            created_by=self.user1['obj'],
        )
        self.assertIn(collection, category.photoblog_collection_set.all())

    def test_reverse_collection_query_accessor(self):
        category = Category.objects.create(name='Test category',
                                           description='Best category!',
                                           created_by=self.user1['obj'])
        Category.objects.create(name='Other cat', description='Not so best',
                                created_by=self.user1['obj'])
        collection = Collection.objects.create(
            title='A bunch of things',
            description="Together in a collection",
            category=category,
            created_by=self.user1['obj'],
        )
        self.assertEqual(category,
                         Category.objects.get(
                             photoblog_collection__title=collection.title))

    def test_reverse_story_relation_accessor(self):
        category = Category.objects.create(name='Test category',
                                           description='Best category!',
                                           created_by=self.user1['obj'])
        story = Story.objects.create(
            title='Tell me a story!',
            description="And I will tell you the truth.",
            category=category,
            text='bla bli blu ble blo',
            created_by=self.user1['obj'],
        )
        self.assertIn(story, category.photoblog_story_set.all())

    def test_reverse_story_query_accessor(self):
        category = Category.objects.create(name='Test category',
                                           description='Best category!',
                                           created_by=self.user1['obj'])
        story = Story.objects.create(
            title='Tell me a story!',
            description="And I will tell you the truth.",
            category=category,
            text='bla bli blu ble blo',
            created_by=self.user1['obj'],
        )
        self.assertEqual(category,
                         Category.objects.get(
                             photoblog_story__title=story.title))


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ImageModelTests(TestCase):
    """Unit tests for Image model."""

    @classmethod
    def setUpTestData(cls):
        user_one = User.objects.create_user(email='test.user@example.com',
                                            username='test_user223',
                                            password='testpassword')
        user_one.save()
        cls.user1 = {
            'obj': user_one,
            'email': 'test.user@example.com',
            'username': 'test_user223',
            'password': 'testpassword'
        }

    def test_anon_cannot_create_image(self):
        image = Image(title='Anon tries to make an image',
                      caption='Anon fails to make an image')
        self.assertRaises(ValidationError, image.save)

    def test_can_create_image(self):
        image = Image.objects.create(
            title='Cover Image',
            caption='Cover image caption',
            created_by=self.user1['obj'],
            image=SimpleUploadedFile(
                name='cover_image.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        self.assertEqual(Image.objects.first(), image)

    def test_slug_gets_populated_properly(self):
        image = Image.objects.create(
            title='Image with a slug title!',
            caption='the caption',
            created_by=self.user1['obj'],
            image=SimpleUploadedFile(
                name='cover_image.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        self.assertEqual(image.slug, 'image-with-a-slug-title')

    def test_can_assign_image_to_entry(self):
        entry = Entry.objects.create(
            title='eeentry',
            description='test desc',
            created_by=self.user1['obj']
        )
        image = Image.objects.create(
            title='Entry Image',
            caption='Entry image caption',
            created_by=self.user1['obj'],
            image=SimpleUploadedFile(
                name='cover_image.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg'
            )
        )
        image.add_to_entry(entry.id)
        self.assertIn(image, entry.images.all())
        self.assertIn(entry, image.entries.all())

    def test_can_assign_image_to_story(self):
        story = Story.objects.create(
            title='my own story',
            description='test story desc',
            text='This is all there is to it',
            created_by=self.user1['obj']
        )
        image = Image.objects.create(
            title='Story image',
            caption='Story image caption',
            created_by=self.user1['obj'],
            image=SimpleUploadedFile(
                name='story_image.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg'
            )
        )
        image.add_to_story(story.id)
        self.assertIn(image, story.images.all())
        self.assertIn(story, image.stories.all())

    def test_image_is_deleted_from_filesystem_on_delete(self):
        image = Image.objects.create(
            title='I am created',
            caption='only to be destroyed',
            created_by=self.user1['obj'],
            image=SimpleUploadedFile(
                name='destroyed.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg'
            )
        )
        path = image.image.file.name
        image.delete()
        with self.assertRaises(FileNotFoundError):
            open(path, 'rb')


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class EntryModelTests(TestCase):
    """Unit tests for Entry model."""

    @classmethod
    def setUpTestData(cls):
        user_one = User.objects.create_user(email='waldo@findme.com',
                                            username='waldotheunfindable',
                                            password='testpassword')
        user_one.save()
        cls.user1 = {
            'obj': user_one,
            'email': 'waldo@findme.com',
            'username': 'waldotheunfindable',
            'password': 'testpassword'
        }
        user_two = User.objects.create_user(email='alexander@macedonia.com',
                                            username='alexanderthegreat',
                                            password='testpassword')
        user_two.save()
        cls.user2 = {
            'obj': user_two,
            'email': 'alexander@macedonia.comm',
            'username': 'alexanderthegreat',
            'password': 'testpassword'
        }

    def test_anon_cannot_create_entry(self):
        entry = Entry(title='Anon tries to make an entry',
                      description='Anon tries to make a nice description',
                      price='100000')
        self.assertRaises(ValidationError, entry.save)

    def test_user_can_create_entry(self):
        entry = Entry.objects.create(
            title="Waldo's first entry!",
            description='Waldo is good at this',
            price='100000',
            created_by=self.user1['obj']
        )
        self.assertEqual(Entry.objects.first(), entry)

    def test_can_set_category(self):
        category = Category.objects.create(name='Test category',
                                           description='Best category!',
                                           created_by=self.user1['obj'])
        entry = Entry.objects.create(
            title='Existential dread',
            slug='existential-dread',
            description="Don't let it set in",
            category=category,
            created_by=self.user1['obj'],
        )
        self.assertEqual(entry.category, category)

    def test_can_set_size(self):
        size = Dimension.objects.create(height=10, length=10)
        entry = Entry.objects.create(
            title='Existential dread',
            slug='existential-dread',
            description="Don't let it set in",
            size=size,
            created_by=self.user1['obj'],
        )
        self.assertEqual(entry.size, size)

    def test_can_assign_entry_to_collection(self):
        collection = Collection.objects.create(
            title='Collect on call',
            description='test collection desc',
            created_by=self.user1['obj']
        )
        entry = Entry.objects.create(
            title='Existential dread',
            description="Don't let it set in",
            created_by=self.user1['obj'],
        )
        entry.add_to_collection(collection.id)
        self.assertIn(entry, collection.entries.all())
        self.assertIn(collection, entry.collections.all())

    def test_set_cover_image_succeeds_with_existing_pk(self):
        entry = Entry.objects.create(
            title='Existential dread',
            description="Don't let it set in",
            price='100000',
            created_by=self.user1['obj'],
        )
        cover = Image.objects.create(
            title='A cover',
            slug='a-cover',
            caption='A cover caption',
            image=SimpleUploadedFile(
                name='a_cover_tale.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
            created_by=entry.created_by
        )
        entry.set_cover_image(cover.pk)
        self.assertEqual(entry.cover, cover)

    def test_set_cover_image_fails_with_non_existing_pk(self):
        entry = Entry.objects.create(
            title='Existential dread',
            description="Don't let it set in",
            price='100000',
            created_by=self.user1['obj'],
        )
        with self.assertRaises(ObjectDoesNotExist):
            entry.set_cover_image(985)

    def test_set_cover_image_succeeds_with_non_existing_object(self):
        entry = Entry.objects.create(
            title='Existential dread part 2',
            description="Don't let it set in once more",
            price='100000',
            created_by=self.user1['obj'],
        )
        cover = Image(
            title='A cover of part 2',
            caption='A cover caption part 2',
            image=SimpleUploadedFile(
                name='a_cover_tale.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
            created_by=entry.created_by
        )
        entry.set_cover_image(cover)
        self.assertEqual(entry.cover, Image.objects.last())

    def test_set_cover_image_succeeds_with_existing_object(self):
        entry = Entry.objects.create(
            title='Existential dread part 2',
            description="Don't let it set in once more",
            price='100000',
            created_by=self.user1['obj'],
        )
        cover = Image.objects.create(
            title='A cover of part 2',
            caption='A cover caption part 2',
            image=SimpleUploadedFile(
                name='a_cover_tale.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
            created_by=entry.created_by
        )
        entry.set_cover_image(cover)
        self.assertEqual(entry.cover, Image.objects.last())


    def test_set_cover_image_method_replaces_old_cover(self):
        entry = Entry.objects.create(
            title='Existential dread',
            slug='existential-dread',
            description="Don't let it set in",
            created_by=self.user1['obj'],
        )
        cover1 = Image.objects.create(
            title='A cover',
            slug='a-cover',
            caption='A cover caption',
            created_by=entry.created_by,
            image=SimpleUploadedFile(
                name='a_cover_tale.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        entry.set_cover_image(cover1.pk)
        cover2 = Image.objects.create(
            title='THE Cover',
            slug='the-cover',
            caption='The realest cover ever',
            created_by=entry.created_by,
            image=SimpleUploadedFile(
                name='cover_story_2.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        entry.set_cover_image(cover2.pk)
        self.assertEqual(entry.cover, cover2)

    def test_cannot_save_entries_with_same_title(self):
        first_entry = Entry(
            title='First entry ever',
            description="It's the first",
            created_by=self.user1['obj']
        )
        second_entry = Entry(
            title='First entry ever',
            description="Second!",
            created_by=self.user1['obj']
        )
        first_entry.save()
        self.assertRaises(ValidationError, second_entry.save)

    def test_add_images_method_fails_without_iterable(self):
        entry = Entry.objects.create(
            title='Entry full of images',
            description="It's the first of its kind",
            created_by=self.user1['obj']
        )
        image = Image(
            title='This is going to fail',
            caption='...spectacularly maybe?',
            created_by=entry.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_entry.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        with self.assertRaises(TypeError):
            entry.add_images(image)

    def test_add_images_succeeds_with_non_existing_object(self):
        entry = Entry.objects.create(
            title='Entry full of images',
            description="It's the first of its kind",
            created_by=self.user1['obj']
        )
        image1 = Image(
            title='This\'ll be really cool',
            caption='and spectacular',
            created_by=entry.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_entry.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        entry.add_images([image1])
        self.assertEqual(image1, entry.images.last())

    def test_add_images_succeeds_with_existing_object(self):
        entry = Entry.objects.create(
            title='Entry full of images',
            description="It's the first of its kind",
            created_by=self.user1['obj']
        )
        image1 = Image.objects.create(
            title='This\'ll be really cool',
            caption='and spectacular',
            created_by=entry.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_entry.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        entry.add_images([image1])
        self.assertEqual(image1, entry.images.last())

    def test_add_images_succeeds_with_existing_image_pk(self):
        entry = Entry.objects.create(
            title='Entry full of images',
            description="It's the first of its kind",
            created_by=self.user1['obj']
        )
        image1 = Image.objects.create(
            title='This\'ll be really cool',
            caption='and spectacular',
            created_by=entry.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_entry.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        entry.add_images([image1.pk])
        self.assertEqual(image1, entry.images.last())

    def test_add_images_noop_with_non_existing_image_pk(self):
        image_count = Image.objects.count()
        entry = Entry.objects.create(
            title='Existential dread',
            description="Don't let it set in",
            price='100000',
            created_by=self.user1['obj'],
        )
        entry.add_images([985])
        self.assertEqual(image_count, Image.objects.count())

    def test_add_images_mixed_input_succeeds(self):
        entry = Entry.objects.create(
            title='Entry full of images',
            description="It's the first of its kind",
            created_by=self.user1['obj']
        )
        image1 = Image.objects.create(
            title='This\'ll be really cool',
            caption='and spectacular',
            created_by=entry.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_entry.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        image2 = Image(
            title='This\'ll be really cool and different',
            caption='and yeah!',
            created_by=entry.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_entry.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        entry.add_images([image1.pk, image2])
        self.assertIn(image1, entry.images.all())
        self.assertIn(entry, image1.entries.all())
        self.assertIn(image2, entry.images.all())
        self.assertIn(entry, image2.entries.all())

    def test_add_images_method_adds_cover_with_pk(self):
        entry = Entry.objects.create(
            title='Entry full of images',
            description="It's the first of its kind",
            created_by=self.user1['obj']
        )
        image = Image.objects.create(
            title='This will be a cover!',
            caption='And a good one at that',
            created_by=entry.created_by,
            image=SimpleUploadedFile(
                name='cover_image_with_a_pk.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        entry.add_images(cover=image.pk)
        self.assertEqual(entry.cover, image)

    def test_add_images_method_creates_cover_with_image_object(self):
        entry = Entry.objects.create(
            title='Entry full of images',
            description="It's the first of its kind",
            created_by=self.user1['obj']
        )
        image = Image(
            title='This will also be a cover!',
            caption='It wont exist until later since this is disposable',
            created_by=entry.created_by,
            image=SimpleUploadedFile(
                name='cover_image_with_a_pk.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        entry.add_images(cover=image)
        self.assertEqual(entry.cover, Image.objects.last())

    def test_add_images_empty_method_does_nothing(self):
        initial_count = Image.objects.count()
        entry = Entry.objects.create(
            title='Entry full of images',
            description="It's the first of its kind",
            created_by=self.user1['obj']
        )
        entry.add_images()
        self.assertEqual(initial_count, Image.objects.count())

    def test_remove_images_empty_method_does_nothing(self):
        entry = Entry.objects.create(
            title='Entry full of images',
            description="It's the first of its kind",
            created_by=self.user1['obj']
        )
        image1 = Image(
            title='This\'ll be really cool',
            caption='and spectacular',
            created_by=entry.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_entry.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        image2 = Image(
            title='This\'ll be really cool and different',
            caption='and yeah!',
            created_by=entry.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_entry.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        entry.add_images([image1, image2])
        entry.remove_images()
        self.assertIn(entry, image1.entries.all())
        self.assertIn(image1, entry.images.all())

    def test_remove_images_removes_image(self):
        entry = Entry.objects.create(
            title='Entry full of images',
            description="It's the first of its kind",
            created_by=self.user1['obj']
        )
        image1 = Image(
            title='This\'ll be really cool',
            caption='and spectacular',
            created_by=entry.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_entry.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        image2 = Image(
            title='This\'ll be really cool and different',
            caption='and yeah!',
            created_by=entry.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_entry.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        entry.add_images((image1, image2,))
        entry.remove_images((image1.pk,))
        self.assertNotIn(entry, image1.entries.all())

    def test_remove_images_method_fails_without_iterable(self):
        entry = Entry.objects.create(
            title='Entry full of images',
            description="It's the first of its kind",
            created_by=self.user1['obj']
        )
        image = Image(
            title='This is going to fail',
            caption='...spectacularly maybe?',
            created_by=entry.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_entry.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        entry.add_images((image,))
        with self.assertRaises(TypeError):
            entry.remove_images(image.pk)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class StoryModelTests(TestCase):
    """Unit tests for Story model."""

    @classmethod
    def setUpTestData(cls):
        user_one = User.objects.create_user(email='waldo@findme.com',
                                            username='waldotheunfindable',
                                            password='testpassword')
        user_one.save()
        cls.user1 = {
            'obj': user_one,
            'email': 'waldo@findme.com',
            'username': 'waldotheunfindable',
            'password': 'testpassword'
        }
        user_two = User.objects.create_user(email='alexander@macedonia.com',
                                            username='alexanderthegreat',
                                            password='testpassword')
        user_two.save()
        cls.user2 = {
            'obj': user_two,
            'email': 'alexander@macedonia.com',
            'username': 'alexanderthegreat',
            'password': 'testpassword'
        }

    def test_anon_cannot_create_story(self):
        story = Story(
            title='Anon tries to make an story',
            description='This is also a headline',
            text="""
            And this text is staggeringly short!
            """
        )
        self.assertRaises(ValidationError, story.save)

    def test_user_can_create_entry(self):
        story = Story.objects.create(
            title="Waldo's first story!",
            description='Waldo is good at this storytelling thing!',
            text='Indeed he is.',
            created_by=self.user1['obj']
        )
        self.assertEqual(Story.objects.first(), story)

    def test_can_set_category(self):
        category = Category.objects.create(name='Test category',
                                           description='Best category!',
                                           created_by=self.user1['obj'])
        story = Story.objects.create(
            title='Existential dread',
            description="Don't let it set in",
            text='This will be a dreadful story it seems',
            category=category,
            created_by=self.user1['obj'],
        )
        self.assertEqual(story.category, category)

    def test_set_cover_image_succeeds_with_existing_pk(self):
        story = Story.objects.create(
            title='Existential dread',
            description="Don't let it set in",
            text='This will be a dreadful story it seems',
            created_by=self.user1['obj'],
        )
        cover = Image.objects.create(
            title='A cover',
            slug='a-cover',
            caption='A cover caption',
            created_by=story.created_by,
            image=SimpleUploadedFile(
                name='a_cover_tale.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        story.set_cover_image(cover.pk)
        self.assertEqual(story.cover, cover)

    def test_set_cover_image_fails_with_non_existing_pk(self):
        story = Story.objects.create(
            title='Existential dread',
            description="Don't let it set in",
            text='This will be a dreadful story it seems',
            created_by=self.user1['obj'],
        )
        with self.assertRaises(ObjectDoesNotExist):
            story.set_cover_image(985)

    def test_set_cover_image_succeeds_with_non_existing_object(self):
        story = Story.objects.create(
            title='Existential dread',
            description="Don't let it set in",
            text='This will be a dreadful story it seems',
            created_by=self.user1['obj'],
        )
        cover = Image(
            title='A cover of part 2',
            caption='A cover caption part 2',
            created_by=story.created_by,
            image=SimpleUploadedFile(
                name='a_cover_tale.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        story.set_cover_image(cover)
        self.assertEqual(story.cover, Image.objects.last())

    def test_set_cover_image_succeeds_with_existing_object(self):
        story = Story.objects.create(
            title='Existential dread',
            description="Don't let it set in",
            text='This will be a dreadful story it seems',
            created_by=self.user1['obj'],
        )
        cover = Image.objects.create(
            title='A cover of part 2',
            caption='A cover caption part 2',
            created_by=story.created_by,
            image=SimpleUploadedFile(
                name='a_cover_tale.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        story.set_cover_image(cover)
        self.assertEqual(story.cover, Image.objects.last())


    def test_set_cover_image_method_replaces_old_cover(self):
        story = Story.objects.create(
            title='Existential dread',
            description="Don't let it set in",
            text='This will be a dreadful story it seems',
            created_by=self.user1['obj'],
        )
        cover1 = Image.objects.create(
            title='A cover',
            slug='a-cover',
            caption='A cover caption',
            created_by=story.created_by,
            image=SimpleUploadedFile(
                name='a_cover_tale.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        story.set_cover_image(cover1.pk)
        cover2 = Image.objects.create(
            title='THE Cover',
            slug='the-cover',
            caption='The realest cover ever',
            created_by=story.created_by,
            image=SimpleUploadedFile(
                name='cover_story_2.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        story.set_cover_image(cover2.pk)
        self.assertEqual(story.cover, cover2)

    def test_cannot_save_entries_with_same_title(self):
        first_story = Story(
            title='First story ever',
            description="It's the first",
            text="First first first first first",
            created_by=self.user1['obj']
        )
        second_story = Story(
            title='First story ever',
            description="Second!",
            text="First first first first first",
            created_by=self.user1['obj']
        )
        first_story.save()
        self.assertRaises(ValidationError, second_story.save)

    def test_add_images_method_fails_without_iterable(self):
        story = Story.objects.create(
            title='Story full of images',
            description="It's the first of its kind",
            text="It's super interesting to tell all these stories",
            created_by=self.user1['obj']
        )
        image = Image(
            title='This is going to fail',
            caption='...spectacularly maybe?',
            created_by=story.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_story.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        with self.assertRaises(TypeError):
            story.add_images(image)

    def test_add_images_succeeds_with_non_existing_object(self):
        story = Story.objects.create(
            title='Story full of images',
            description="It's the first of its kind",
            text="It's super interesting to tell all these stories",
            created_by=self.user1['obj'],
        )
        image1 = Image(
            title='This\'ll be really cool',
            caption='and spectacular',
            created_by=story.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_story.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        story.add_images([image1])
        self.assertEqual(image1, story.images.last())

    def test_add_images_succeeds_with_existing_object(self):
        story = Story.objects.create(
            title='Story full of images',
            description="It's the first of its kind",
            text="It's super interesting to tell all these stories",
            created_by=self.user1['obj']
        )
        image1 = Image.objects.create(
            title='This\'ll be really cool',
            caption='and spectacular',
            created_by=story.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_story.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        story.add_images([image1])
        self.assertEqual(image1, story.images.last())

    def test_add_images_succeeds_with_existing_image_pk(self):
        story = Story.objects.create(
            title='Story full of images',
            description="It's the first of its kind",
            text="It's super interesting to tell all these stories",
            created_by=self.user1['obj']
        )
        image1 = Image.objects.create(
            title='This\'ll be really cool',
            caption='and spectacular',
            created_by=story.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_story.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        story.add_images([image1.pk])
        self.assertEqual(image1, story.images.last())

    def test_add_images_noop_with_non_existing_image_pk(self):
        image_count = Image.objects.count()
        story = Story.objects.create(
            title='Story full of images',
            description="It's the first of its kind",
            text="It's super interesting to tell all these stories",
            created_by=self.user1['obj']
        )
        story.add_images([985])
        self.assertEqual(image_count, Image.objects.count())

    def test_add_images_mixed_input_succeeds(self):
        story = Story.objects.create(
            title='Story full of images',
            description="It's the first of its kind",
            text="It's super interesting to tell all these stories",
            created_by=self.user1['obj']
        )
        image1 = Image.objects.create(
            title='This\'ll be really cool',
            caption='and spectacular',
            created_by=story.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_story.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        image2 = Image(
            title='This\'ll be really cool and different',
            caption='and yeah!',
            created_by=story.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_story.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        story.add_images([image1.pk, image2])
        self.assertIn(image1, story.images.all())
        self.assertIn(story, image1.stories.all())
        self.assertIn(image2, story.images.all())
        self.assertIn(story, image2.stories.all())

    def test_add_images_method_adds_cover_with_pk(self):
        story = Story.objects.create(
            title='Story full of images',
            description="It's the first of its kind",
            text="It's super interesting to tell all these stories",
            created_by=self.user1['obj']
        )
        image = Image.objects.create(
            title='This will be a cover!',
            caption='And a good one at that',
            created_by=story.created_by,
            image=SimpleUploadedFile(
                name='cover_image_with_a_pk.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        story.add_images(cover=image.pk)
        self.assertEqual(story.cover, image)

    def test_add_images_method_creates_cover_with_image_object(self):
        story = Story.objects.create(
            title='Story full of images',
            description="It's the first of its kind",
            text="It's super interesting to tell all these stories",
            created_by=self.user1['obj']
        )
        image = Image(
            title='This will also be a cover!',
            caption='It wont exist until later since this is disposable',
            created_by=story.created_by,
            image=SimpleUploadedFile(
                name='cover_image_with_a_pk.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        story.add_images(cover=image)
        self.assertEqual(story.cover, Image.objects.last())

    def test_add_images_empty_method_does_nothing(self):
        initial_count = Image.objects.count()
        story = Story.objects.create(
            title='Story full of images',
            description="It's the first of its kind",
            text="It's super interesting to tell all these stories",
            created_by=self.user1['obj']
        )
        story.add_images()
        self.assertEqual(initial_count, Image.objects.count())

    def test_remove_images_empty_method_does_nothing(self):
        story = Story.objects.create(
            title='Story full of images',
            description="It's the first of its kind",
            text="It's super interesting to tell all these stories",
            created_by=self.user1['obj']
        )
        image1 = Image(
            title='This\'ll be really cool',
            caption='and spectacular',
            created_by=story.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_story.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        image2 = Image(
            title='This\'ll be really cool and different',
            caption='and yeah!',
            created_by=story.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_story.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        story.add_images([image1, image2])
        story.remove_images()
        self.assertIn(story, image1.stories.all())
        self.assertIn(image1, story.images.all())

    def test_remove_images_removes_image(self):
        story = Story.objects.create(
            title='Story full of images',
            description="It's the first of its kind",
            text="It's super interesting to tell all these stories",
            created_by=self.user1['obj']
        )
        image1 = Image(
            title='This\'ll be really cool',
            caption='and spectacular',
            created_by=story.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_story.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        image2 = Image(
            title='This\'ll be really cool and different',
            caption='and yeah!',
            created_by=story.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_story.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        story.add_images((image1, image2,))
        story.remove_images((image1.pk,))
        self.assertNotIn(story, image1.stories.all())

    def test_remove_images_method_fails_without_iterable(self):
        story = Story.objects.create(
            title='Story full of images',
            description="It's the first of its kind",
            text="It's super interesting to tell all these stories",
            created_by=self.user1['obj']
        )
        image = Image(
            title='This is going to fail',
            caption='...spectacularly maybe?',
            created_by=story.created_by,
            image=SimpleUploadedFile(
                name='image_added_to_story.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        story.add_images((image,))
        with self.assertRaises(TypeError):
            story.remove_images(image.pk)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class CollectionModelTests(TestCase):
    """Unit tests for Collection model."""

    @classmethod
    def setUpTestData(cls):
        user_one = User.objects.create_user(email='waldo@findme.com',
                                            username='waldotheunfindable',
                                            password='testpassword')
        user_one.save()
        cls.user1 = {
            'obj': user_one,
            'email': 'waldo@findme.com',
            'username': 'waldotheunfindable',
            'password': 'testpassword'
        }
        user_two = User.objects.create_user(email='alexander@macedonia.com',
                                            username='alexanderthegreat',
                                            password='testpassword')
        user_two.save()
        cls.user2 = {
            'obj': user_two,
            'email': 'alexander@macedonia.comm',
            'username': 'alexanderthegreat',
            'password': 'testpassword'
        }

    def test_anon_cannot_create_collection(self):
        collection = Collection(
            title='Anon tries to make an collection',
            description='This is also a headline',
        )
        self.assertRaises(ValidationError, collection.save)

    def test_user_can_create_entry(self):
        collection = Collection.objects.create(
            title="Waldo's first collection!",
            description='Waldo is good at this storytelling thing!',
            created_by=self.user1['obj']
        )
        self.assertEqual(Collection.objects.first(), collection)

    def test_can_set_category(self):
        category = Category.objects.create(name='Test category',
                                           description='Best category!',
                                           created_by=self.user1['obj'])
        collection = Collection.objects.create(
            title='Existential dread',
            description="Don't let it set in",
            category=category,
            created_by=self.user1['obj'],
        )
        self.assertEqual(collection.category, category)

    def test_set_cover_image_succeeds_with_existing_pk(self):
        collection = Collection.objects.create(
            title='Existential dread',
            description="Don't let it set in",
            created_by=self.user1['obj'],
        )
        cover = Image.objects.create(
            title='A cover',
            slug='a-cover',
            caption='A cover caption',
            created_by=collection.created_by,
            image=SimpleUploadedFile(
                name='a_cover_tale.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        collection.set_cover_image(cover.pk)
        self.assertEqual(collection.cover, cover)

    def test_set_cover_image_fails_with_non_existing_pk(self):
        collection = Collection.objects.create(
            title='Existential dread',
            description="Don't let it set in",
            created_by=self.user1['obj'],
        )
        with self.assertRaises(ObjectDoesNotExist):
            collection.set_cover_image(985)

    def test_set_cover_image_succeeds_with_non_existing_object(self):
        collection = Collection.objects.create(
            title='Existential dread',
            description="Don't let it set in",
            created_by=self.user1['obj'],
        )
        cover = Image(
            title='A cover of part 2',
            caption='A cover caption part 2',
            created_by=collection.created_by,
            image=SimpleUploadedFile(
                name='a_cover_tale.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        collection.set_cover_image(cover)
        self.assertEqual(collection.cover, Image.objects.last())

    def test_set_cover_image_succeeds_with_existing_object(self):
        collection = Collection.objects.create(
            title='Existential dread',
            description="Don't let it set in",
            created_by=self.user1['obj'],
        )
        cover = Image.objects.create(
            title='A cover of part 2',
            caption='A cover caption part 2',
            created_by=collection.created_by,
            image=SimpleUploadedFile(
                name='a_cover_tale.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        collection.set_cover_image(cover)
        self.assertEqual(collection.cover, Image.objects.last())


    def test_set_cover_image_method_replaces_old_cover(self):
        collection = Collection.objects.create(
            title='Existential dread',
            description="Don't let it set in",
            created_by=self.user1['obj'],
        )
        cover1 = Image.objects.create(
            title='A cover',
            slug='a-cover',
            caption='A cover caption',
            created_by=collection.created_by,
            image=SimpleUploadedFile(
                name='a_cover_tale.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        collection.set_cover_image(cover1.pk)
        cover2 = Image.objects.create(
            title='THE Cover',
            slug='the-cover',
            caption='The realest cover ever',
            created_by=collection.created_by,
            image=SimpleUploadedFile(
                name='cover_story_2.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg',
            ),
        )
        collection.set_cover_image(cover2.pk)
        self.assertEqual(collection.cover, cover2)

    def test_cannot_save_entries_with_same_title(self):
        first_story = Collection(
            title='First collection ever',
            description="It's the first",
            created_by=self.user1['obj']
        )
        second_story = Collection(
            title='First collection ever',
            description="Second!",
            created_by=self.user1['obj']
        )
        first_story.save()
        self.assertRaises(ValidationError, second_story.save)

    def test_add_entries_method_fails_without_iterable(self):
        collection = Collection.objects.create(
            title='Collection full of entries',
            description="It's the first of its kind",
            created_by=self.user1['obj']
        )
        entry = Entry(
            title='This is going to fail',
            description='...spectacularly maybe?',
            created_by=collection.created_by,
        )
        with self.assertRaises(TypeError):
            collection.add_entries(entry)

    def test_add_entries_fails_with_non_existing_object(self):
        collection = Collection.objects.create(
            title='Collection full of entries',
            description="It's the first of its kind",
            created_by=self.user1['obj'],
        )
        entry = Entry(
            title='This will be really cool',
            description='and spectacular',
            created_by=collection.created_by,
        )
        collection.add_entries([entry])
        found = Entry.objects.filter(
            title__icontains='This will be really cool')
        self.assertNotIn(found, Entry.objects.all())

    def test_add_entries_succeeds_with_existing_object(self):
        collection = Collection.objects.create(
            title='Collection full of entries',
            description="It's the first of its kind",
            created_by=self.user1['obj']
        )
        entry = Entry.objects.create(
            title='This\'ll be really cool',
            description='and spectacular',
            created_by=collection.created_by,
        )
        collection.add_entries([entry])
        self.assertEqual(entry, collection.entries.last())

    def test_add_entries_succeeds_with_existing_entry_pk(self):
        collection = Collection.objects.create(
            title='Collection full of entries',
            description="It's the first of its kind",
            created_by=self.user1['obj']
        )
        entry = Entry.objects.create(
            title='This\'ll be really cool',
            description='and spectacular',
            created_by=collection.created_by,
        )
        collection.add_entries([entry.pk])
        self.assertEqual(entry, collection.entries.last())

    def test_add_entries_noop_with_non_existing_entry_pk(self):
        entry_count = Entry.objects.count()
        collection = Collection.objects.create(
            title='Collection full of images',
            description="It's the first of its kind",
            created_by=self.user1['obj']
        )
        collection.add_entries([985])
        self.assertEqual(entry_count, Entry.objects.count())

    def test_add_entries_mixed_input_succeeds(self):
        collection = Collection.objects.create(
            title='Collection full of images',
            description="It's the first of its kind",
            created_by=self.user1['obj']
        )
        entry1 = Entry.objects.create(
            title='This\'ll be really cool',
            description='and spectacular',
            created_by=collection.created_by,
        )
        entry2 = Entry.objects.create(
            title='This\'ll be really cool and different',
            description='and yeah!',
            created_by=collection.created_by,
        )
        collection.add_entries([entry1.pk, entry2])
        self.assertIn(entry1, collection.entries.all())
        self.assertIn(collection, entry1.collections.all())
        self.assertIn(entry2, collection.entries.all())
        self.assertIn(collection, entry2.collections.all())

    def test_remove_entries_empty_method_does_nothing(self):
        collection = Collection.objects.create(
            title='Collection full of entries',
            description="It's the first of its kind",
            created_by=self.user1['obj']
        )
        entry1 = Entry.objects.create(
            title='This\'ll be really cool',
            description='and spectacular',
            created_by=collection.created_by,
        )
        entry2 = Entry.objects.create(
            title='This\'ll be really cool and different',
            description='and yeah!',
            created_by=collection.created_by,
        )
        collection.add_entries([entry1, entry2])
        collection.remove_entries()
        self.assertIn(collection, entry1.collections.all())
        self.assertIn(collection, entry2.collections.all())

    def test_remove_entries_removes_entry(self):
        collection = Collection.objects.create(
            title='Collection full of entries',
            description="It's the first of its kind",
            created_by=self.user1['obj']
        )
        entry1 = Entry.objects.create(
            title='This\'ll be really cool',
            description='and spectacular',
            created_by=collection.created_by,
        )
        entry2 = Entry.objects.create(
            title='This\'ll be really cool and different',
            description='and yeah!',
            created_by=collection.created_by,
        )
        collection.add_entries((entry1, entry2,))
        collection.remove_entries((entry1.pk,))
        self.assertNotIn(entry1, collection.entries.all())

    def test_remove_entries_method_fails_without_iterable(self):
        collection = Collection.objects.create(
            title='Collection full of entries',
            description="It's the first of its kind",
            created_by=self.user1['obj']
        )
        entry = Entry.objects.create(
            title='This\'ll be really cool',
            description='and spectacular',
            created_by=collection.created_by,
        )
        collection.add_entries((entry,))
        with self.assertRaises(TypeError):
            collection.remove_entries(entry.pk)
