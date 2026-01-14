"""
Тесты для логики расчёта цен
"""
from decimal import Decimal
from django.test import TestCase

from calculator.models import PricingSettings, CleaningPrice, PromoText, DryCleaningService
from calculator.services import (
    calculate_room_bathroom_price,
    calculate_cleaning_price_by_level,
    calculate_dry_cleaning_price,
    calculate_total_price,
    PriceCalculationError
)


class PriceCalculationTests(TestCase):
    """Тесты расчёта цен"""

    def setUp(self):
        """Настройка тестовых данных"""
        # Настройки цен за комнату и туалет
        self.pricing = PricingSettings.objects.create(
            price_per_room=Decimal("20"),
            price_per_bathroom=Decimal("15")
        )

        # Цены для уборки
        self.price_basic_50 = CleaningPrice.objects.create(
            level="basic",
            title="До 50 m²",
            area_from=0,
            area_to=50,
            price=Decimal("1400"),
            old_price=Decimal("1750"),
            sort_order=1
        )

        self.price_basic_80 = CleaningPrice.objects.create(
            level="basic",
            title="50–80 m²",
            area_from=51,
            area_to=80,
            price=Decimal("1640"),
            sort_order=2
        )

        self.price_basic_plus = CleaningPrice.objects.create(
            level="basic",
            title="+10 m²",
            area_from=81,
            area_to=None,
            price=Decimal("120"),
            sort_order=3
        )

        # Текст акции
        self.promo = PromoText.objects.create(
            text="20% do 15.01",
            is_active=True
        )

    def test_room_bathroom_price(self):
        """Тест расчёта цены за комнаты и туалеты"""
        price = calculate_room_bathroom_price(
            rooms=2,
            bathrooms=1,
            pricing=self.pricing
        )
        # 2 * 20 + 1 * 15 = 55
        self.assertEqual(price, Decimal("55.00"))

    def test_room_bathroom_price_zero(self):
        """Тест с нулевыми значениями"""
        price = calculate_room_bathroom_price(
            rooms=0,
            bathrooms=0,
            pricing=self.pricing
        )
        self.assertEqual(price, Decimal("0.00"))

    def test_room_bathroom_price_negative(self):
        """Тест с отрицательными значениями (должна быть ошибка)"""
        with self.assertRaises(PriceCalculationError):
            calculate_room_bathroom_price(
                rooms=-1,
                bathrooms=0,
                pricing=self.pricing
            )

    def test_calculate_cleaning_price_40(self):
        """Тест расчёта цены для площади 40 м² (0-50)"""
        price = calculate_cleaning_price_by_level(Decimal("40"), "basic")
        self.assertEqual(price, Decimal("1400"))

    def test_calculate_cleaning_price_50(self):
        """Тест расчёта цены для площади 50 м² (0-50)"""
        price = calculate_cleaning_price_by_level(Decimal("50"), "basic")
        self.assertEqual(price, Decimal("1400"))

    def test_calculate_cleaning_price_60(self):
        """Тест расчёта цены для площади 60 м² (51-80)"""
        price = calculate_cleaning_price_by_level(Decimal("60"), "basic")
        self.assertEqual(price, Decimal("1640"))

    def test_calculate_cleaning_price_80(self):
        """Тест расчёта цены для площади 80 м² (51-80)"""
        price = calculate_cleaning_price_by_level(Decimal("80"), "basic")
        self.assertEqual(price, Decimal("1640"))

    def test_calculate_cleaning_price_81(self):
        """Тест расчёта цены для площади 81 м² (>80, 1 шаг)"""
        price = calculate_cleaning_price_by_level(Decimal("81"), "basic")
        self.assertEqual(price, Decimal("1760"))

    def test_calculate_cleaning_price_90(self):
        """Тест расчёта цены для площади 90 м² (>80, 1 шаг)"""
        price = calculate_cleaning_price_by_level(Decimal("90"), "basic")
        self.assertEqual(price, Decimal("1760"))

    def test_calculate_cleaning_price_91(self):
        """Тест расчёта цены для площади 91 м² (>80, 2 шага)"""
        price = calculate_cleaning_price_by_level(Decimal("91"), "basic")
        self.assertEqual(price, Decimal("1880"))

    def test_calculate_cleaning_price_100(self):
        """Тест расчёта цены для площади 100 м² (>80, 2 шага)"""
        price = calculate_cleaning_price_by_level(Decimal("100"), "basic")
        self.assertEqual(price, Decimal("1880"))

    def test_calculate_cleaning_price_101(self):
        """Тест расчёта цены для площади 101 м² (>80, 3 шага)"""
        price = calculate_cleaning_price_by_level(Decimal("101"), "basic")
        self.assertEqual(price, Decimal("2000"))

    def test_dry_cleaning_price_item(self):
        """Тест расчёта цены химчистки за единицу"""
        item = DryCleaningService.objects.create(
            name="Диван",
            price=Decimal("800"),
            unit="item",
            is_active=True
        )

        price = calculate_dry_cleaning_price([item])
        self.assertEqual(price, Decimal("800.00"))

    def test_dry_cleaning_price_m2(self):
        """Тест расчёта цены химчистки за м²"""
        item = DryCleaningService.objects.create(
            name="Ковер",
            price=Decimal("120"),
            unit="m2",
            is_active=True
        )

        areas = {item.id: Decimal("10")}  # 10 м²
        price = calculate_dry_cleaning_price([item], areas)
        # 120 * 10 = 1200
        self.assertEqual(price, Decimal("1200.00"))

    def test_dry_cleaning_price_m2_no_area(self):
        """Тест химчистки за м² без указания площади (должна быть ошибка)"""
        item = DryCleaningService.objects.create(
            name="Ковер",
            price=Decimal("120"),
            unit="m2",
            is_active=True
        )

        with self.assertRaises(PriceCalculationError):
            calculate_dry_cleaning_price([item])

    def test_total_price_all_services(self):
        """Тест расчёта итоговой цены со всеми услугами"""
        # Комнаты: 2, туалеты: 1 = 55
        # Уборка: 50 м² = 1400
        # Химчистка: диван 800
        # Итого: 55 + 1400 + 800 = 2255

        item = DryCleaningService.objects.create(
            name="Диван",
            price=Decimal("800"),
            unit="item",
            is_active=True
        )

        total = calculate_total_price(
            rooms=2,
            bathrooms=1,
            area=Decimal("50"),
            cleaning_level="basic",
            dry_cleaning_items=[item]
        )

        self.assertEqual(total, Decimal("2255.00"))

    def test_total_price_only_rooms(self):
        """Тест расчёта только за комнаты"""
        total = calculate_total_price(
            rooms=3,
            bathrooms=2
        )
        # 3 * 20 + 2 * 15 = 90
        self.assertEqual(total, Decimal("90.00"))

    def test_total_price_only_cleaning(self):
        """Тест расчёта только за уборку"""
        total = calculate_total_price(
            area=Decimal("60"),
            cleaning_level="basic"
        )
        # 60 м² по новой формуле = 1640 (51-80 м²)
        self.assertEqual(total, Decimal("1640.00"))

