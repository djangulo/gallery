# pylint: disable=invalid-name
"""Translation options for photoblog app."""
from modeltranslation.translator import register, TranslationOptions
from photoblog.models import (
    Category,
    Collection,
    Entry,
    Image,
    Story,
)


@register(Entry)
class EntryTranslationOptions(TranslationOptions):
    """Translation options for Entry model."""
    fields = ('title', 'slug', 'description',)


@register(Story)
class StoryTranslationOptions(TranslationOptions):
    """Translation options for Story model."""
    fields = ('title', 'slug', 'description', 'text',)


@register(Collection)
class CollectionTranslationOptions(TranslationOptions):
    """Translation options for Collection model."""
    fields = ('title', 'slug', 'description',)


@register(Image)
class ImageTranslationOptions(TranslationOptions):
    """Translation options for Image model."""
    fields = ('title', 'caption')


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    """Translation options for Category model."""
    fields = ('name', 'slug', 'description',)
