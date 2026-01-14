"""
Сервис для работы с ценами уборки
Вся логика выбора цены (не расчёта!) вынесена сюда
"""
import math
from decimal import Decimal
from typing import Optional, List

from .models import CleaningPrice, PricingSettings, DryCleaningService


class PriceCalculationError(Exception):
    """Ошибка выбора/расчёта цены"""
    pass


def validate_positive_int(value, field_name: str) -> int:
    """Валидация положительного целого числа"""
    if value is None:
        return 0
    if not isinstance(value, int):
        raise PriceCalculationError(f"{field_name} must be int")
    if value < 0:
        raise PriceCalculationError(f"{field_name} cannot be negative")
    return value


def validate_positive_decimal(value, field_name: str) -> Decimal:
    """Валидация положительного Decimal"""
    if value is None:
        return Decimal("0")
    try:
        decimal_value = Decimal(value)
        if decimal_value < 0:
            raise PriceCalculationError(f"{field_name} cannot be negative")
        return decimal_value
    except (ValueError, TypeError):
        raise PriceCalculationError(f"{field_name} must be a valid number")


# ----------------------------
# БАЗОВЫЙ РАСЧЁТ: комнаты + санузлы
# ----------------------------
def calculate_room_bathroom_price(
    rooms: int,
    bathrooms: int,
    pricing: Optional[PricingSettings] = None
) -> Decimal:
    """
    Расчёт цены за комнаты и туалеты
    """
    rooms = validate_positive_int(rooms, "rooms")
    bathrooms = validate_positive_int(bathrooms, "bathrooms")

    if pricing is None:
        pricing = PricingSettings.get_settings()

    total = (
        Decimal(rooms) * pricing.price_per_room +
        Decimal(bathrooms) * pricing.price_per_bathroom
    )

    return total.quantize(Decimal("0.01"))


# ----------------------------
# РАСЧЁТ ЦЕНЫ ДЛЯ УБОРКИ (по формуле с данными из базы)
# ----------------------------
def calculate_cleaning_price_by_level(area: Decimal, level: str) -> Decimal:
    """
    Рассчитать цену уборки по площади и уровню
    Использует цены из базы данных (CleaningPrice)
    
    Логика:
    - 0-50 м² → цена из CleaningPrice с area_to=50
    - 51-80 м² → цена из CleaningPrice с area_from=50, area_to=80
    - >80 м² → цена_51_80 + (steps * цена_за_10м²), где цена_за_10м² из CleaningPrice с area_from=80
    
    Args:
        area: Площадь в м²
        level: Уровень уборки (basic, general, general_plus)
    
    Returns:
        Рассчитанная цена
    """
    area = validate_positive_decimal(area, "area")
    area_int = int(area)

    # Получаем все активные цены для данного уровня
    prices = CleaningPrice.objects.filter(
        level=level,
        is_active=True
    ).order_by('sort_order', 'area_from')

    if not prices.exists():
        raise PriceCalculationError(
            f"No prices configured for level '{level}' in admin panel"
        )

    # Ищем цену для 0-50 м² (area_from=0 или None, area_to=50)
    price_0_50 = None
    for price in prices:
        if (price.area_from is None or price.area_from == 0) and price.area_to == 50:
            price_0_50 = price.price
            break

    # Ищем цену для 51-80 м² (area_from=51, area_to=80)
    price_51_80 = None
    for price in prices:
        if price.area_from == 51 and price.area_to == 80:
            price_51_80 = price.price
            break

    # Ищем цену за +10 м² (для площади >80)
    # Это цена с area_from >= 80 (обычно 81) и area_to is None, или в названии есть "+10"
    price_per_step = None
    for price in prices:
        # Ищем цену для шага: area_from >= 80 (или 81) и area_to is None
        if price.area_from is not None and price.area_from >= 80 and price.area_to is None:
            price_per_step = price.price
            break
        # Или ищем по названию "+10" или "10 м" или "за 10"
        elif ("+10" in price.title.lower() or "+ 10" in price.title.lower() or 
              "10 м" in price.title.lower() or "за 10" in price.title.lower() or
              "10м" in price.title.lower()):
            price_per_step = price.price
            break

    # Если не нашли цену за шаг, вычисляем её на основе существующих цен
    if price_per_step is None:
        if price_51_80 and price_0_50:
            # Средняя цена за 10 м² = (цена_51_80 - цена_0_50) / 30 * 10
            price_per_step = (price_51_80 - price_0_50) / Decimal("30") * Decimal("10")
        elif price_51_80:
            # Если есть только цена за 51-80, используем примерно 1/8 от неё
            price_per_step = price_51_80 / Decimal("8")
        elif price_0_50:
            # Если есть только цена за 0-50, используем примерно 1/5 от неё
            price_per_step = price_0_50 / Decimal("5")
        else:
            raise PriceCalculationError(
                f"No prices found for level '{level}' to calculate step price"
            )

    # Расчёт цены
    if area_int <= 50:
        if price_0_50 is None:
            raise PriceCalculationError(
                f"Price for 0-50 m² not found for level '{level}'"
            )
        return price_0_50
    
    elif area_int <= 80:
        if price_51_80 is None:
            # Если нет цены для 51-80, используем цену для 0-50
            if price_0_50 is None:
                raise PriceCalculationError(
                    f"Price for 51-80 m² not found for level '{level}'"
                )
            return price_0_50
        return price_51_80
    
    else:
        # >80 м² → price_51_80 + (steps * price_per_step)
        if price_51_80 is None:
            if price_0_50 is None:
                raise PriceCalculationError(
                    f"Base price not found for level '{level}'"
                )
            base_price = price_0_50
        else:
            base_price = price_51_80
        
        if price_per_step is None:
            # Если не нашли цену за шаг, используем расчёт на основе базовой цены
            # Берём среднюю цену за м² из диапазона 51-80
            if price_51_80:
                # Примерная цена за 10 м² = (цена_51_80 - цена_0_50) / 30 * 10
                if price_0_50:
                    price_per_step = (price_51_80 - price_0_50) / Decimal("30") * Decimal("10")
                else:
                    price_per_step = price_51_80 / Decimal("8")  # Примерно 1/8 от цены за 80 м²
            else:
                # Fallback: используем базовую цену / 8
                price_per_step = base_price / Decimal("8")
        
        # Для площадей >80 м² считаем шаги по 10 м²
        # Например: 81-90 = 1 шаг, 91-100 = 2 шага, 101-110 = 3 шага
        extra_area = area_int - 80
        # Если extra_area = 0, то шагов нет (но это не должно произойти, т.к. area_int > 80)
        # Если extra_area = 1-10, то 1 шаг
        # Если extra_area = 11-20, то 2 шага
        # И так далее
        if extra_area <= 0:
            steps = 0
        else:
            # Округляем вверх: ceil((extra_area) / 10)
            # Для 1-10 м² = 1 шаг, для 11-20 м² = 2 шага
            steps = math.ceil(extra_area / 10.0)
        
        price = base_price + (Decimal(str(steps)) * price_per_step)
        return price.quantize(Decimal("0.01"))


# ----------------------------
# ВЫБОР ЦЕНЫ ДЛЯ УБОРКИ (по площади и уровню) - для других уровней
# ----------------------------
def get_cleaning_price_for_area(
    area: Decimal,
    level: str = "basic"
) -> Optional[CleaningPrice]:
    """
    Получить цену уборки для заданной площади и уровня
    Для уровня "basic" используется формула calculate_cleaning_price_by_area
    
    Args:
        area: Площадь в м²
        level: Уровень уборки (basic, general, general_plus)
    
    Returns:
        CleaningPrice объект или None если не найдено
    """
    area = validate_positive_decimal(area, "area")
    area_int = int(area)

    # Для всех уровней используем формулу с данными из базы
    if level in ["basic", "general", "general_plus"]:
        # Используем формулу для всех уровней (цены берутся из базы)
        return None  # Будем обрабатывать отдельно в API

    # Для других уровней ищем в базе
    prices = CleaningPrice.objects.filter(
        level=level,
        is_active=True
    ).order_by('sort_order', 'area_from')

    # Ищем подходящую цену
    for price in prices:
        # Диапазон: area_from <= area <= area_to
        if price.area_from is not None and price.area_to is not None:
            if price.area_from <= area_int <= price.area_to:
                return price
        
        # От area_from и выше (без верхней границы)
        elif price.area_from is not None and price.area_to is None:
            if area_int >= price.area_from:
                return price
        
        # До area_to (без нижней границы)
        elif price.area_from is None and price.area_to is not None:
            if area_int <= price.area_to:
                return price

    # Если ничего не найдено, возвращаем первую цену (или None)
    return prices.first()


# ----------------------------
# ХИМЧИСТКА (расчёт по выбранным объектам)
# ----------------------------
def calculate_dry_cleaning_price(
    items: List[DryCleaningService],
    areas: Optional[dict] = None
) -> Decimal:
    """
    Расчёт цены за химчистку
    
    Args:
        items: Список объектов химчистки
        areas: Словарь {service_id: area} для объектов с единицей "m2"
    
    Returns:
        Общая цена за химчистку
    """
    if areas is None:
        areas = {}

    total = Decimal("0")

    for item in items:
        if not item.is_active:
            continue

        if item.unit == "item":
            total += item.price
        elif item.unit == "m2":
            if item.id not in areas:
                raise PriceCalculationError(
                    f"Area required for dry cleaning service '{item.name}' (unit: m²)"
                )
            area = validate_positive_decimal(areas[item.id], f"area for {item.name}")
            total += item.price * area
        else:
            raise PriceCalculationError(
                f"Unknown unit '{item.unit}' for DryCleaningService {item.id}"
            )

    return total.quantize(Decimal("0.01"))


# ----------------------------
# ИТОГОВАЯ ЦЕНА (комнаты + уборка + химчистка)
# ----------------------------
def calculate_total_price(
    *,
    rooms: int = 0,
    bathrooms: int = 0,
    area: Optional[Decimal] = None,
    cleaning_level: str = "basic",
    dry_cleaning_items: Optional[List[DryCleaningService]] = None,
    dry_cleaning_areas: Optional[dict] = None,
) -> Decimal:
    """
    Расчёт итоговой цены за все услуги
    
    Args:
        rooms: Количество комнат
        bathrooms: Количество туалетов
        area: Площадь в м² (для выбора цены уборки)
        cleaning_level: Уровень уборки (basic, general, general_plus)
        dry_cleaning_items: Список объектов химчистки
        dry_cleaning_areas: Словарь {service_id: area} для химчистки
    
    Returns:
        Итоговая цена
    """
    total = Decimal("0")

    # 1. Комнаты и туалеты
    if rooms > 0 or bathrooms > 0:
        total += calculate_room_bathroom_price(rooms, bathrooms)

    # 2. Уборка (выбор цены по площади)
    if area is not None and area > 0:
        if cleaning_level in ["basic", "general", "general_plus"]:
            # Для всех уровней используем формулу
            total += calculate_cleaning_price_by_level(area, cleaning_level)
        else:
            # Для других уровней ищем в базе
            cleaning_price = get_cleaning_price_for_area(area, cleaning_level)
            if cleaning_price:
                total += cleaning_price.price
            else:
                raise PriceCalculationError(
                    f"No price found for area {area} m² and level '{cleaning_level}'"
                )

    # 3. Химчистка
    if dry_cleaning_items:
        total += calculate_dry_cleaning_price(
            dry_cleaning_items,
            dry_cleaning_areas
        )

    return total.quantize(Decimal("0.01"))

