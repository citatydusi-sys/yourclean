from django.contrib import admin
from .models import (
    PricingSettings, CleaningType, ExtraService, DryCleaningService,
    CleaningPrice, PromoText, Order, Review, Advantage, GalleryItem, CompanyInfo, DateDiscount
)


@admin.register(PricingSettings)
class PricingSettingsAdmin(admin.ModelAdmin):
    """Админка для настройки цен"""
    list_display = ('price_per_room', 'price_per_bathroom', 'updated_at')
    fields = ('price_per_room', 'price_per_bathroom')
    
    def has_add_permission(self, request):
        """Разрешить создание только одной записи"""
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        """Запретить удаление записи"""
        return False


@admin.register(CleaningType)
class CleaningTypeAdmin(admin.ModelAdmin):
    """Админка для типов уборки"""
    list_display = ("name", "base_price_per_m2", "coefficient", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    list_editable = ("is_active",)


@admin.register(ExtraService)
class ExtraServiceAdmin(admin.ModelAdmin):
    """Админка для дополнительных услуг"""
    list_display = ("name", "price_type", "price", "is_active")
    list_filter = ("price_type", "is_active")
    search_fields = ("name",)
    list_editable = ("is_active",)


@admin.register(DryCleaningService)
class DryCleaningServiceAdmin(admin.ModelAdmin):
    """Админка для химчистки"""
    list_display = ("name", "price", "unit", "is_active")
    list_filter = ("unit", "is_active")
    search_fields = ("name",)
    list_editable = ("is_active",)


@admin.register(CleaningPrice)
class CleaningPriceAdmin(admin.ModelAdmin):
    """Админка для цен уборки"""
    list_display = ("level", "title", "area_from", "area_to", "old_price", "price", "is_active")
    list_filter = ("level", "is_active")
    search_fields = ("title",)
    list_editable = ("is_active", "price", "old_price")
    fieldsets = (
        ("Основная информация", {
            "fields": ("level", "title", "is_active", "sort_order")
        }),
        ("Диапазон площади", {
            "fields": ("area_from", "area_to"),
            "description": "Оставьте пустым для диапазона без ограничений"
        }),
        ("Цены", {
            "fields": ("old_price", "price"),
            "description": "old_price - для отображения акции (зачёркнутая цена)"
        }),
    )


@admin.register(PromoText)
class PromoTextAdmin(admin.ModelAdmin):
    """Админка для текста акции"""
    list_display = ("text", "is_active")
    list_display_links = ("text",)
    list_editable = ("is_active",)
    
    def has_add_permission(self, request):
        """Разрешить создание только одной записи"""
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        """Запретить удаление записи"""
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Админка для заявок"""
    list_display = (
        'id', 'name', 'phone', 'cleaning_level', 'area', 
        'total_price', 'status', 'created_at'
    )
    list_filter = ('status', 'cleaning_level', 'created_at')
    search_fields = ('name', 'phone', 'email', 'address')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status',)
    fieldsets = (
        ('Контактные данные', {
            'fields': ('name', 'phone', 'email')
        }),
        ('Параметры уборки', {
            'fields': ('cleaning_level', 'area', 'rooms', 'bathrooms')
        }),
        ('Цена', {
            'fields': ('total_price',)
        }),
        ('Дополнительная информация', {
            'fields': ('address', 'desired_date', 'desired_time', 'comment'),
            'classes': ('collapse',)
        }),
        ('Статус', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Все поля только для чтения после создания"""
        if obj:  # Если объект уже создан
            return self.readonly_fields + ('name', 'phone', 'email', 'cleaning_level', 
                                         'area', 'rooms', 'bathrooms', 'total_price')
        return self.readonly_fields


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Админка для отзывов"""
    list_display = ('name', 'rating', 'date', 'is_active', 'created_at')
    list_filter = ('rating', 'is_active', 'date')
    search_fields = ('name', 'text')
    list_editable = ('is_active',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'text', 'rating', 'photo_url', 'is_active')
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'date')


@admin.register(Advantage)
class AdvantageAdmin(admin.ModelAdmin):
    """Админка для преимуществ"""
    list_display = ('title', 'icon', 'is_active', 'sort_order')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    list_editable = ('is_active', 'sort_order')
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'icon', 'is_active', 'sort_order')
        }),
    )


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    """Админка для галереи"""
    list_display = ('caption', 'is_active', 'sort_order', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('caption',)
    list_editable = ('is_active', 'sort_order')
    fieldsets = (
        ('Фотографии', {
            'fields': ('before_image', 'after_image', 'caption', 'is_active', 'sort_order')
        }),
    )


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    """Админка для информации о компании"""
    list_display = ('phone', 'email', 'address', 'updated_at')
    fieldsets = (
        ('Контактная информация', {
            'fields': ('phone', 'email', 'address')
        }),
        ('Социальные сети', {
            'fields': ('whatsapp', 'telegram', 'instagram', 'facebook')
        }),
        ('Карта', {
            'fields': ('map_lat', 'map_lng')
        }),
    )


@admin.register(DateDiscount)
class DateDiscountAdmin(admin.ModelAdmin):
    """Админка для скидок по датам"""
    list_display = ('date', 'discount_percent', 'is_active', 'created_at')
    list_filter = ('is_active', 'date', 'discount_percent')
    search_fields = ('date',)
    ordering = ('-date',)
    date_hierarchy = 'date'
    list_editable = ('is_active',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('date', 'discount_percent', 'is_active'),
            'description': 'Вы можете добавлять несколько скидок на разные даты. На одну дату можно установить только одну скидку.'
        }),
    )
