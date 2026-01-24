from modeltranslation.translator import register, TranslationOptions

from .models import (
    Advantage,
    CleaningPrice,
    CleaningType,
    DryCleaningService,
    ExtraService,
    GalleryItem,
    PromoText,
)


@register(CleaningType)
class CleaningTypeTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(DryCleaningService)
class DryCleaningServiceTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(ExtraService)
class ExtraServiceTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(CleaningPrice)
class CleaningPriceTranslationOptions(TranslationOptions):
    fields = ("title",)


@register(Advantage)
class AdvantageTranslationOptions(TranslationOptions):
    fields = ("title", "description")


@register(GalleryItem)
class GalleryItemTranslationOptions(TranslationOptions):
    fields = ("caption",)


@register(PromoText)
class PromoTextTranslationOptions(TranslationOptions):
    fields = ("text",)
