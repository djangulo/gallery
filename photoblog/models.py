# pylint: disable=arguments-differ, no-member, attribute-defined-outside-init, invalid-name
"""Models for photoblog app."""
from typing import List, NewType

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# types used in models
DATETIME_VAR = NewType('DateTime', timezone.datetime)

def image_directory_path(instance, filename):
    """Saves the image in filesystem as described by return statement"""
    yyyy_mm = timezone.now().strftime('%Y-%m')
    return f'user_{instance.created_by.id}/{yyyy_mm}/{filename}'


class Dimension(models.Model):
    """Dimension model to assign sizes to art pieces."""
    MILIMETERS = 'mm'
    CENTIMETERS = 'cm'
    METERS = 'm'
    INCHES = 'in'
    FEET = 'ft'
    TWO_DIMENSIONS = '2d'
    THREE_DIMENSIONS = '3d'
    CONVERSIONS = {
        'm':  {'ft': 3.2808, 'in': 39.3701, 'cm': 100.0000, 'mm': 1000.0000},
        'ft': {'m' : 0.3048, 'in': 12.0000, 'cm':  30.4800, 'mm':  304.8000},
        'in': {'m' : 0.0254, 'ft':  0.0833, 'cm':   2.5400, 'mm':   25.4000},
        'cm': {'m' : 0.0100, 'ft':  0.0328, 'in':   0.3937, 'mm':   10.0000},
        'mm': {'m' : 0.0010, 'ft':  0.0033, 'in':   0.0394, 'cm':    0.1000},
    }
    UNIT_CHOICES = (
        (MILIMETERS, _('Milimeters')),
        (CENTIMETERS, _('Centimeters')),
        (METERS, _('Meters')),
        (INCHES, _('Inches')),
        (FEET, _('Feet')),
    )
    unit = models.CharField(max_length=2, choices=UNIT_CHOICES,
                            default=INCHES)
    height = models.FloatField(null=True, blank=False, verbose_name=_('height'))
    length = models.FloatField(null=True, blank=False, verbose_name=_('length'))
    width = models.FloatField(null=True, blank=True, verbose_name=_('width'),
                              help_text='If your art piece were 3 dimensional'
                                        ', how wide (thick) would it be')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   blank=False, null=True,
                                   on_delete=models.SET_NULL)

    def __str__(self):
        if self.width is not None:
            return f'h: {self.height} {self.unit}, l: {self.length}  '\
                    f'{self.unit}, w: {self.width}  {self.unit}'
        return f'h: {self.height} {self.unit}, l: {self.length} '\
                f'{self.unit}'

    def to_object(self):
        if self.width is not None:
            return {
                'height': self.height,
                'length': self.length,
                'width': self.width,
                'unit': self.unit
            }
        return {
                    'height': self.height,
                    'length': self.length,
                    'unit': self.unit
                }

    def convert_unit(self, unit: str = None):
        """Changes the dimension's unit to the one specified by 'unit'.

        Keyword arguments:
        unit -- unit to convert to. Must be one of: 'mm', 'cm', 'm',
                'in', 'ft'. (default 'in')
        """
        if unit not in [u[0] for u in self.UNIT_CHOICES]:
            raise ValidationError("Unit provided must be one of: 'mm', 'cm', 'm', 'in', 'ft'.")
        current_unit = self.unit
        self.unit = unit
        factor = self.CONVERSIONS[current_unit][unit]
        if self.height:
            self.height = self.height * factor
        if self.length:
            self.length = self.length * factor
        if self.width:
            self.width = self.width * factor
        self.save()
        return f'Units updated: {self.__str__()}'

    def display_as_unit(self, unit=None):
        """Returns the dimension's units as the one specified by
        'unit'. Does not write changes to the database.

        Keyword arguments:
        unit -- unit to convert to. Must be one of: 'mm', 'cm', 'm',
                'in', 'ft'. (default 'in')
        """
        if unit not in [u[0] for u in self.UNIT_CHOICES]:
            raise ValidationError("Unit provided must be one of: 'mm', 'cm', 'm', 'in', 'ft'.")
        current_unit = self.unit
        factor = self.CONVERSIONS[current_unit][unit]
        if self.height:
            height = self.height * factor
        if self.length:
            length = self.length * factor
        if self.width:
            width = self.width * factor
        if width is not None:
            return f'h: {height} {unit}, l: {length}  {unit}, w: {width}  {unit}'
        return f'h: {height} {unit}, l: {length} {unit}'


class Category(models.Model):
    """Category model, self-explanatory."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True)
    description = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   blank=False, null=True,
                                   on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def clean(self, *args, **kwargs):
        self.slug = slugify(self.name_en)
        if self.name_es:
            self.slug_es = slugify(self.name_es)
        super(Category, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Category, self).save(*args, **kwargs)


class Image(models.Model):
    """Image model, for entire application."""
    title = models.CharField(max_length=100, blank=False, unique=True)
    slug = models.SlugField(blank=True, default='')
    caption = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=image_directory_path, blank=False,
                              null=True)
    entries = models.ManyToManyField('photoblog.Entry', related_name='images',
                                     blank=True)
    stories = models.ManyToManyField('photoblog.Story', related_name='images',
                                     blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='images',
                             on_delete=models.SET_NULL, null=True, blank=False
                            )

    class Meta:
        verbose_name = 'image'
        verbose_name_plural = 'images'

    def __str__(self):
        return f'id: {self.id}, {self.title}'

    def clean(self, *args, **kwargs):
        self.slug = slugify(self.title_en)
        self.slug_en = self.slug
        if self.title_es:
            self.slug_es = slugify(self.title_es)
        super(Image, self).clean(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.image.delete(save=False)
        super(Image, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Image, self).save(*args, **kwargs)

    def add_to_entry(self, entry_id):
        """Adds image to an entry object, specified by the 'pk'
        argument.

        Keyword arguments:
        entry_id -- primary key to Entry object
        """
        entry = Entry.objects.get(pk=entry_id)
        self.entries.add(entry)
        self.save()
        return entry

    def add_to_story(self, story_id: int) -> None:
        """Adds image to a story object, specified by the 'pk'
        argument.

        Keyword arguments:
        story_id -- primary key to Entry object
        """
        story = Story.objects.get(pk=story_id)
        self.stories.add(story)
        self.save()
        return story


class Item(models.Model):
    """Base model for Entry, Story and Collection."""
    title = models.CharField(max_length=100, blank=False)
    slug = models.SlugField(blank=True, default='')
    description = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    category = models.ForeignKey(Category, related_name='%(app_label)s_%(class)s_set',
                                 related_query_name='%(app_label)s_%(class)s',
                                 on_delete=models.SET_NULL, null=True,
                                 blank=True)
    cover = models.ForeignKey(Image, related_name='cover_of_%(app_label)s_%(class)s',
                              related_query_name='%(app_label)s_%(class)s',
                              on_delete=models.SET_NULL, null=True,
                              blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='%(app_label)s_%(class)s_set',
                             related_query_name='%(app_label)s_%(class)s',
                             on_delete=models.SET_NULL, null=True,
                             blank=False)

    class Meta:
        abstract = True


    def __str__(self):
        return f'{self.title_en}'

    def clean(self, *args, **kwargs):
        self.slug = slugify(self.title_en)
        if self.title_es:
            self.slug_es = slugify(self.title_es)
        super(Item, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Item, self).save(*args, **kwargs)

    def publish(self, time: DATETIME_VAR = timezone.now()):
        """Changes draft to be publicly viewable.

        Keyword arguments:
        time -- Set a time for publishing (default timezone.now())
        """
        self.published_at = time
        self.save()

    def un_publish(self) -> None:
        """Removes the object from public view, keeps it as draft."""
        self.published_at = None
        self.save()

    def get_cover(self):
        """Returns the cover image of the model."""
        return self.cover

    def set_cover_image(self, image: int or Image = None) -> bool:
        """Creates or retrieves the cover image in question, and sets
        as the cover image of the model.

        Keyword arguments:
        image -- image primary key of image object to be added
        """
        if image is not None:
            if isinstance(image, int):
                img = Image.objects.get(pk=image)
                self.cover = img
                self.save()
            elif image.id:
                img = Image.objects.get(pk=image.id)
                self.cover = img
                self.save()
            else:
                img = Image.objects.create(
                    title=image.title,
                    title_es=image.title_es,
                    caption=image.caption,
                    caption_es=image.caption_es,
                    created_by=image.created_by,
                    image=image.image,
                )
                self.cover = img
                self.save()
            return True
        return False

    def add_images(self, images: List[int or Image] = None,
                   cover: int or Image = None) -> None:
        """Gets, or creates images and assigns it to its image set.
        Accepts a mixed iterable of ints or Image objects. Note that
        the Image objects in the 'images' iterable are disposed of, and
        the DB objects will be different from these. Will fail silently
        if one of the image pks passed does not exist.

        Keyword arguments:
        images -- photoblog.models.Image or int iterable object. (default None)
        cover -- photoblog.models.Image or int that will be set as cover
        """
        ids, non_id_images, existing_ids = [], [], []
        if images is not None:
            try:
                iter(images)
            except TypeError:
                raise TypeError(f'{type(images)} is not iterable')
            for i in images:
                try:
                    ids.append(i.id)
                    if not i.id:
                        non_id_images.append(i)
                except AttributeError:
                    ids.append(i)
            existing_ids = list(
                Image.objects.filter(id__in=ids).values_list('id', flat=True))
            created_images = Image.objects.bulk_create(non_id_images)
            existing_ids.extend([j.id for j in created_images])
        if cover is not None:
            if images is None or cover in images:
                if isinstance(cover, int):
                    self.set_cover_image(cover)
                elif cover.id:
                    self.set_cover_image(cover.id)
            else:
                if isinstance(cover, int):
                    self.set_cover_image(cover)
                    if cover not in existing_ids:
                        existing_ids.append(cover)
                elif cover.id:
                    self.set_cover_image(cover.id)
                    if cover.id not in existing_ids:
                        existing_ids.append(cover)
                else:
                    cov = Image.objects.create(
                        title=cover.title,
                        title_es=cover.title_es,
                        caption=cover.caption,
                        caption_es=cover.caption_es,
                        created_by=cover.created_by,
                        image=cover.image,
                    )
                    self.set_cover_image(cov.id)
                    if cov.id not in existing_ids:
                        existing_ids.append(cov.id)
        self.images.add(*existing_ids)

    def remove_images(self, pks: List[int] = None) -> None:
        """Removes images from image set, as specified by the 'pks'
        keyword.

        Keyword arguments:
        pks -- iterable of primary keys of images to be removed
               (default None)
        """
        if pks is not None:
            try:
                iter(pks)
            except TypeError:
                raise TypeError(f'{type(pks)} is not iterable')
            self.images.remove(*pks)


class Entry(Item):
    """Entry model. Refers to a photoblog entry (whatever art piece it may be."""
    price = models.FloatField(null=True, blank=True)
    size = models.ForeignKey('photoblog.Dimension', related_name='entries',
                             blank=True, null=True, on_delete=models.SET_NULL)
    collections = models.ManyToManyField('photoblog.Collection',
                                         related_name='entries', blank=True)

    class Meta(Item.Meta):
        verbose_name = 'entry'
        verbose_name_plural = 'entries'
        ordering = ('-created_at',)
        unique_together = (('title', 'created_by'), ('slug', 'created_by'),)
        permissions = (
            ('publish_entry', _('can publish entry')),
            ('unpublish_entry', _('can un-publish entry')),
            ('view_unpublished', _('can view entry drafts')),
        )

    def add_to_collection(self, collection_id):
        """Adds entry to a collection object, specified by the 'pk'
        argument.

        Keyword arguments:
        collection_id -- primary key to Collection object
        """
        collection = Collection.objects.get(pk=collection_id)
        self.collections.add(collection)
        self.save()
        return collection


class Story(Item):
    """Story model, collection of images with text."""
    text = models.TextField(blank=False, null=False)

    class Meta(Item.Meta):
        verbose_name = 'story'
        verbose_name_plural = 'stories'
        ordering = ('-created_at',)
        unique_together = (('title', 'created_by'), ('slug', 'created_by'),)
        permissions = (
            ('publish_story', 'can publish story'),
            ('unpublish_story', 'can un-publish story'),
            ('view_unpublished', 'can view story drafts'),
        )


class Collection(Item):
    """Collection, Multiple Entry instances with a cover."""
    class Meta(Item.Meta):
        verbose_name = 'collection'
        verbose_name_plural = 'collections'
        ordering = ('-created_at',)
        unique_together = (('title', 'created_by'), ('slug', 'created_by'),)
        permissions = (
            ('publish_collection', 'can publish collection'),
            ('unpublish_collection', 'can un-publish collection'),
            ('view_unpublished', 'can view collection drafts'),
        )

    def add_entries(self, entries: List[int or Entry] = None) -> None:
        """Gets entries and assigns it to its entry set. Accepts a
        mixed iterable of ints or Entry objects. The ints should point
        to the id of an Entry object. Will fail silently if one of the
        entry pks passed does not exist. 

        Keyword arguments:
        entries -- photoblog.models.Entry or int iterable object.
        """
        ids, existing_ids = [], []
        if entries is not None:
            try:
                iter(entries)
            except TypeError:
                raise TypeError(f'{type(entries)} is not iterable')
            for i in entries:
                try:
                    ids.append(i.id)
                except AttributeError:
                    ids.append(i)
            existing_ids = Entry.objects.filter(id__in=ids)
        self.entries.add(*existing_ids)

    def remove_entries(self, pks: List[int] = None) -> None:
        """Removes entries from entry set, as specified by the 'pks'
        keyword.

        Keyword arguments:
        pks -- iterable of primary keys of entries to be removed
               (default None)
        """
        if pks is not None:
            try:
                iter(pks)
            except TypeError:
                raise TypeError(f'{type(pks)} is not iterable')
            self.entries.remove(*pks)
