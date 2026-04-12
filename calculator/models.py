from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class PricingSettings(models.Model):
    """Настройки цен для калькулятора уборки"""
    price_per_room = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Цена за одну комнату"
    )
    price_per_bathroom = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Цена за один туалет"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Настройки цен"
        verbose_name_plural = "Настройки цен"

    def __str__(self):
        return f"Цена за комнату: {self.price_per_room}, Цена за туалет: {self.price_per_bathroom}"

    @classmethod
    def get_settings(cls):
        """Получить единственную запись настроек или создать новую"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class CleaningType(models.Model):
    """Типы уборки"""
    name = models.CharField(max_length=100, verbose_name="Тип уборки")
    base_price_per_m2 = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Базовая цена за м²"
    )
    coefficient = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.00,
        verbose_name="Коэффициент сложности"
    )
    image = models.ImageField(
        upload_to='cleaning_types/',
        blank=True,
        null=True,
        verbose_name="Фото типа уборки",
        help_text="Загрузите изображение, которое будет отображаться на сайте"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Тип уборки"
        verbose_name_plural = "Типы уборки"
        ordering = ['name']

    def __str__(self):
        return self.name


class ExtraService(models.Model):
    """Дополнительные услуги"""
    PRICE_TYPE_CHOICES = (
        ("fixed", "Фиксированная цена"),
        ("per_m2", "Цена за м²"),
    )

    name = models.CharField(max_length=100, verbose_name="Дополнительная услуга")
    price_type = models.CharField(
        max_length=10,
        choices=PRICE_TYPE_CHOICES,
        default="fixed",
        verbose_name="Тип цены"
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Цена"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Дополнительная услуга"
        verbose_name_plural = "Дополнительные услуги"
        ordering = ['name']

    def __str__(self):
        return self.name


class DryCleaningService(models.Model):
    """Химчистка"""
    UNIT_CHOICES = (
        ("item", "За единицу"),
        ("m2", "За м²"),
    )

    name = models.CharField(max_length=100, verbose_name="Объект химчистки")
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Цена"
    )
    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        default="item",
        verbose_name="Единица измерения"
    )
    image = models.ImageField(
        upload_to='dry_cleaning/',
        blank=True,
        null=True,
        verbose_name="Фото услуги",
        help_text="Фото будет показано в блоке услуг"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Химчистка"
        verbose_name_plural = "Химчистка"
        ordering = ['name']

    def __str__(self):
        return self.name


class CleaningPrice(models.Model):
    """Готовые цены для уборки по уровням и диапазонам площади"""
    CLEANING_LEVELS = (
        ("basic", "Basic"),
        ("general", "General"),
        ("general_plus", "General Plus"),
    )

    level = models.CharField(
        max_length=20,
        choices=CLEANING_LEVELS,
        verbose_name="Уровень уборки"
    )

    title = models.CharField(
        max_length=50,
        verbose_name="Название диапазона",
        help_text="Например: До 50 m², 50–80 m², +10 m²"
    )

    area_from = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Площадь от (м²)"
    )
    area_to = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Площадь до (м²)"
    )

    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Старая цена (для акции)"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Текущая цена"
    )

    is_active = models.BooleanField(default=True, verbose_name="Активна")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")

    class Meta:
        verbose_name = "Цена уборки"
        verbose_name_plural = "Цены уборки"
        ordering = ['level', 'sort_order', 'area_from']

    def __str__(self):
        return f"{self.get_level_display()} — {self.title} ({self.price} Kč)"


class PromoText(models.Model):
    """Текст акции/промо"""
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    text = models.CharField(
        max_length=100,
        default="20% do 15.01",
        verbose_name="Текст акции",
        help_text="Например: 20% do 15.01, AKCE, SLEVA, -350 Kč"
    )

    class Meta:
        verbose_name = "Текст акции"
        verbose_name_plural = "Тексты акций"

    def __str__(self):
        return self.text if self.is_active else f"{self.text} (неактивна)"

    @classmethod
    def get_active(cls):
        """Получить активный текст акции"""
        return cls.objects.filter(is_active=True).first()


class Order(models.Model):
    """Заявка клиента на уборку"""
    STATUS_CHOICES = (
        ('new', 'Новая'),
        ('confirmed', 'Подтверждена'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    )

    CLEANING_LEVELS = (
        ("basic", "Basic"),
        ("general", "General"),
        ("general_plus", "General Plus"),
    )

    # Контактные данные
    name = models.CharField(max_length=100, verbose_name="Имя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    
    # Параметры расчёта
    cleaning_level = models.CharField(
        max_length=20,
        choices=CLEANING_LEVELS,
        verbose_name="Уровень уборки"
    )
    area = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="Площадь (м²)"
    )
    rooms = models.PositiveIntegerField(default=0, verbose_name="Количество комнат")
    bathrooms = models.PositiveIntegerField(default=0, verbose_name="Количество туалетов")
    
    # Цена
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Итоговая цена"
    )
    
    # Дополнительная информация
    address = models.TextField(blank=True, null=True, verbose_name="Адрес")
    desired_date = models.DateField(blank=True, null=True, verbose_name="Желаемая дата")
    desired_time = models.TimeField(blank=True, null=True, verbose_name="Желаемое время")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    extra_services = models.TextField(
        blank=True,
        null=True,
        verbose_name="Дополнительные услуги",
        help_text="Перечень выбранных дополнительных услуг"
    )
    dry_cleaning_items = models.TextField(
        blank=True,
        null=True,
        verbose_name="Объекты химчистки",
        help_text="Выбранные позиции химчистки с количеством"
    )
    
    # Статус и даты
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Статус заказа"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-created_at']

    # Скидка
    applied_discount_percent = models.PositiveIntegerField(
        default=0,
        verbose_name="Применённая скидка (%)",
        help_text="Скидка, применённая при выборе даты"
    )
    
    def __str__(self):
        return f"Заявка #{self.id} от {self.name} ({self.total_price} Kč)"


class Review(models.Model):
    """Отзывы клиентов"""
    name = models.CharField(max_length=100, verbose_name="Имя клиента")
    text = models.TextField(verbose_name="Текст отзыва")
    rating = models.PositiveIntegerField(
        default=5,
        verbose_name="Рейтинг",
        help_text="От 1 до 5"
    )
    photo_url = models.URLField(blank=True, null=True, verbose_name="Фото клиента (URL)")
    date = models.DateField(auto_now_add=True, verbose_name="Дата")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.name} - {self.rating}★"


class Advantage(models.Model):
    """Преимущества компании"""
    title = models.CharField(max_length=100, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    icon = models.CharField(
        max_length=10,
        default="✨",
        verbose_name="Иконка (эмодзи или текст)",
        help_text="Например: 🌿, ⚡, 📅, ✅"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Преимущество"
        verbose_name_plural = "Преимущества"
        ordering = ['sort_order', 'created_at']

    def __str__(self):
        return self.title


class GalleryItem(models.Model):
    """Галерея до/после уборки"""
    before_image = models.URLField(verbose_name="Фото до (URL)")
    after_image = models.URLField(verbose_name="Фото после (URL)")
    caption = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Подпись"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Фото до/после"
        verbose_name_plural = "Галерея до/после"
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.caption or f"Фото #{self.id}"


class CompanyInfo(models.Model):
    """Информация о компании (singleton)"""
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    address = models.TextField(verbose_name="Адрес")
    
    # Социальные сети
    whatsapp = models.CharField(max_length=100, blank=True, null=True, verbose_name="WhatsApp")
    telegram = models.CharField(max_length=100, blank=True, null=True, verbose_name="Telegram")
    instagram = models.CharField(max_length=100, blank=True, null=True, verbose_name="Instagram")
    facebook = models.CharField(max_length=100, blank=True, null=True, verbose_name="Facebook")
    
    # Координаты для карты
    map_lat = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name="Широта (для карты)"
    )
    map_lng = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name="Долгота (для карты)"
    )
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Информация о компании"
        verbose_name_plural = "Информация о компании"

    def __str__(self):
        return "Информация о компании"

    @classmethod
    def get_info(cls):
        """Получить единственную запись или создать новую"""
        info, created = cls.objects.get_or_create(pk=1)
        return info


class DateDiscount(models.Model):
    """Скидки по датам для календаря"""
    date = models.DateField(verbose_name="Дата")
    discount_percent = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Скидка (%)",
        help_text="0 = нет скидки, 10 = -10%, 20 = -20% и т.д."
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Скидка по дате"
        verbose_name_plural = "Скидки по датам"
        ordering = ['date']
        unique_together = [['date', 'discount_percent']]  # Можно иметь разные скидки на одну дату, но не дубликаты

    def __str__(self):
        if self.discount_percent > 0:
            return f"{self.date} — -{self.discount_percent}%"
        return f"{self.date} — без скидки"


class ServiceCategory(models.Model):
    """Категории услуг для шага 2 калькулятора (карточки с фото)"""
    SERVICE_CHOICES = [
        ('cleaning', 'Уборка помещений'),
        ('drycleaning', 'Химчистка мебели'),
        ('cargo', 'Грузоперевозки'),
        ('shoe_cleaning', 'Химчистка обуви'),
    ]

    slug = models.CharField(
        max_length=50,
        choices=SERVICE_CHOICES,
        unique=True,
        verbose_name="Тип услуги"
    )
    title = models.CharField(max_length=200, verbose_name="Заголовок карточки")
    description = models.CharField(max_length=500, verbose_name="Описание карточки")
    image = models.ImageField(
        upload_to='service_categories/',
        blank=True,
        null=True,
        verbose_name="Фото карточки",
        help_text="Рекомендуемый размер: 600×400 px"
    )
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Категория услуги"
        verbose_name_plural = "Категории услуг (карточки)"
        ordering = ['sort_order']

    def __str__(self):
        return self.get_slug_display()


class CargoTariff(models.Model):
    """Тарифы грузоперевозок"""
    name = models.CharField(max_length=200, verbose_name="Название тарифа")
    price_per_hour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена за час (крон)"
    )
    min_hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=1.0,
        verbose_name="Минимальное количество часов"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Тариф грузоперевозки"
        verbose_name_plural = "Грузоперевозки — Тарифы"
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f"{self.name} — {self.price_per_hour} Kč/час (мин. {self.min_hours} ч.)"


class CargoOption(models.Model):
    """Дополнительные опции грузоперевозок"""
    name = models.CharField(max_length=200, verbose_name="Название опции")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Фиксированная цена (крон)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Доп. опция грузоперевозки"
        verbose_name_plural = "Грузоперевозки — Доп. опции"
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f"{self.name} — {self.price} Kč"


class ShoeCleaningService(models.Model):
    """Химчистка обуви"""
    name = models.CharField(max_length=200, verbose_name="Тип обуви")
    price_per_pair = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена за пару (крон)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Химчистка обуви"
        verbose_name_plural = "Химчистка обуви"
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f"{self.name} — {self.price_per_pair} Kč/пара"
