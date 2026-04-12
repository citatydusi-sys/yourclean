from modeltranslation.translator import register, TranslationOptions

from .models import (
    Advantage,
    CleaningPrice,
    CleaningType,
    DryCleaningService,
    ExtraService,
    GalleryItem,
    PromoText,
    CargoTariff,
    CargoOption,
    ShoeCleaningService,
    ServiceCategory,
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


@register(CargoTariff)
class CargoTariffTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(CargoOption)
class CargoOptionTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(ShoeCleaningService)
class ShoeCleaningServiceTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(ServiceCategory)
class ServiceCategoryTranslationOptions(TranslationOptions):
    fields = ("title", "description")
