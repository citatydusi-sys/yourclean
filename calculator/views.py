from django.shortcuts import render
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation
import traceback
from .models import (
    PricingSettings, PromoText, ExtraService, DryCleaningService, CleaningPrice,
    Review, Advantage, GalleryItem, CompanyInfo, CleaningType,
    CargoTariff, CargoOption, ShoeCleaningService, ServiceCategory
)
from .services import (
    calculate_cleaning_price_by_level,
    calculate_room_bathroom_price,
    PriceCalculationError,
)


def home_view(request):
    """View для главной страницы"""
    company_info = CompanyInfo.get_info()
    advantages = Advantage.objects.filter(is_active=True).order_by('sort_order')[:4]
    reviews = Review.objects.filter(is_active=True).order_by('-date', '-created_at')[:6]
    cleaning_types = CleaningType.objects.filter(is_active=True)[:6]
    dry_cleaning_services = DryCleaningService.objects.filter(is_active=True)[:6]
    
    context = {
        'company_info': company_info,
        'advantages': advantages,
        'reviews': reviews,
        'cleaning_types': cleaning_types,
        'dry_cleaning_services': dry_cleaning_services,
    }
    
    return render(request, 'calculator/home.html', context)


def about_view(request):
    """View для страницы О нас"""
    company_info = CompanyInfo.get_info()
    advantages = Advantage.objects.filter(is_active=True).order_by('sort_order')
    gallery_items = GalleryItem.objects.filter(is_active=True).order_by('sort_order')[:6]
    drycleaning_services = DryCleaningService.objects.filter(is_active=True).order_by('name')
    
    context = {
        'company_info': company_info,
        'advantages': advantages,
        'gallery_items': gallery_items,
        'drycleaning_services': drycleaning_services,
    }
    
    return render(request, 'calculator/about.html', context)


def calculator_view(request):
    """View для калькулятора уборки"""
    # Получаем настройки цен
    pricing = PricingSettings.get_settings()
    
    # Получаем данные для шаблона из админки
    company_info = CompanyInfo.get_info()
    advantages = Advantage.objects.filter(is_active=True).order_by('sort_order')[:4]
    reviews = Review.objects.filter(is_active=True).order_by('-date', '-created_at')[:3]
    promo_text = PromoText.get_active()
    
    service_categories = ServiceCategory.objects.filter(is_active=True)
    categories_dict = {cat.slug: cat for cat in service_categories}

    context = {
        'pricing': pricing,
        'company_info': company_info,
        'advantages': advantages,
        'reviews': reviews,
        'promo_text': promo_text,
        'max_rooms': 30,
        'max_bathrooms': 30,
        'service_categories': categories_dict,
    }
    
    return render(request, 'calculator/calculator.html', context)



def calculate_price_api(request):
    """API endpoint для получения итоговой цены уборки со всеми параметрами"""
    # Получаем параметры из запроса
    level = request.GET.get("level", "basic")
    area_str = request.GET.get("area", "0")
    rooms_str = request.GET.get("rooms", "0")
    bathrooms_str = request.GET.get("bathrooms", "0")
    extra_services_str = request.GET.get("extra_services", "")  # JSON array of IDs
    dry_cleaning_str = request.GET.get("dry_cleaning", "")  # JSON object {id: area}

    # Валидация уровня
    valid_levels = ["basic", "general", "general_plus"]
    if level not in valid_levels:
        return JsonResponse({
            "error": f"Invalid level. Must be one of: {', '.join(valid_levels)}"
        }, status=400)

    # Валидация и парсинг параметров
    try:
        area = Decimal(area_str) if area_str else Decimal("0")
        rooms = int(rooms_str) if rooms_str else 0
        bathrooms = int(bathrooms_str) if bathrooms_str else 0
        
        if area < 0 or rooms < 0 or bathrooms < 0:
            return JsonResponse({
                "error": "Значения не могут быть отрицательными"
            }, status=400)
            
        if rooms > 30 or bathrooms > 30:
            return JsonResponse({
                "error": "Максимум 30 комнат и 30 туалетов"
            }, status=400)
        
        # Проверка максимальной площади (например, 50000 м²)
        if area > 50000:
            return JsonResponse({
                "error": "Площадь не может превышать 50000 м²"
            }, status=400)
            
    except (InvalidOperation, ValueError, TypeError) as e:
        return JsonResponse({
            "error": f"Некорректные значения параметров: {str(e)}"
        }, status=400)

    # Парсинг дополнительных услуг
    extra_services = []
    if extra_services_str:
        try:
            import json
            extra_service_ids = json.loads(extra_services_str)
            if isinstance(extra_service_ids, list):
                extra_services = ExtraService.objects.filter(
                    id__in=extra_service_ids,
                    is_active=True
                )
        except (json.JSONDecodeError, ValueError):
            pass

    # Парсинг химчистки
    dry_cleaning_items = []
    dry_cleaning_areas = {}
    if dry_cleaning_str:
        try:
            import json
            dry_cleaning_data = json.loads(dry_cleaning_str)
            if isinstance(dry_cleaning_data, dict):
                dry_cleaning_items = DryCleaningService.objects.filter(
                    id__in=dry_cleaning_data.keys(),
                    is_active=True
                )
                dry_cleaning_areas = {
                    int(k): Decimal(str(v)) 
                    for k, v in dry_cleaning_data.items()
                }
        except (json.JSONDecodeError, ValueError, TypeError):
            pass

    # Расчёт итоговой цены
    try:
        # 1. Цена за комнаты и туалеты
        room_bathroom_price = calculate_room_bathroom_price(rooms, bathrooms)
        
        # 2. Цена за уборку (по площади и уровню)
        cleaning_price = Decimal("0")
        if area > 0:
            try:
                cleaning_price = calculate_cleaning_price_by_level(area, level)
            except PriceCalculationError as e:
                # Если нет цен для уборки, возвращаем понятную ошибку
                error_msg = str(e)
                # Улучшаем сообщение об ошибке
                if "not found" in error_msg.lower() or "not configured" in error_msg.lower():
                    return JsonResponse({
                        "error": f"Не настроены цены для уровня '{level}' и площади {int(area)} м². Проверьте настройки в админке."
                    }, status=400)
                return JsonResponse({
                    "error": f"Ошибка расчёта: {error_msg}"
                }, status=400)
            except Exception as e:
                # Другие ошибки при расчёте
                import traceback
                error_msg = str(e)
                print(f"Error calculating cleaning price: {error_msg}")
                print(traceback.format_exc())
                # Более понятное сообщение для пользователя
                return JsonResponse({
                    "error": f"Ошибка расчёта цены для площади {int(area)} м². Проверьте настройки в админке или попробуйте другую площадь."
                }, status=500)
        
        # 3. Цена за дополнительные услуги
        extra_price = Decimal("0")
        for service in extra_services:
            if service.price_type == "fixed":
                extra_price += service.price
            elif service.price_type == "per_m2" and area > 0:
                extra_price += service.price * area
        
        # 4. Цена за химчистку
        dry_cleaning_price = Decimal("0")
        for item in dry_cleaning_items:
            if item.unit == "item":
                # Для "item" умножаем цену на количество
                quantity = dry_cleaning_areas.get(item.id, Decimal("1"))
                dry_cleaning_price += item.price * quantity
            elif item.unit == "m2" and item.id in dry_cleaning_areas:
                # Для "m2" умножаем цену на площадь
                dry_cleaning_price += item.price * dry_cleaning_areas[item.id]
        
        # Итоговая цена
        total_price = room_bathroom_price + cleaning_price + extra_price + dry_cleaning_price
        
        # Получаем текст акции и старую цену (для уборки)
        promo = PromoText.get_active()
        old_price = None
        
        # Старая цена берётся из CleaningPrice для текущего уровня и площади
        # Для площадей >80 м² старая цена не применяется (т.к. используется формула)
        if area > 0 and int(area) <= 80:
            price_obj = CleaningPrice.objects.filter(
                level=level,
                is_active=True,
                area_from__lte=int(area),
                area_to__gte=int(area)
            ).first()
            
            if not price_obj:
                # Ищем ближайший диапазон
                if int(area) <= 50:
                    price_obj = CleaningPrice.objects.filter(
                        level=level,
                        is_active=True,
                        area_from__lte=0,
                        area_to=50
                    ).first()
                elif int(area) <= 80:
                    price_obj = CleaningPrice.objects.filter(
                        level=level,
                        is_active=True,
                        area_from=51,
                        area_to=80
                    ).first()
            
            if price_obj and price_obj.old_price:
                # Старая цена только для уборки, не для всего
                old_price = str(price_obj.old_price + room_bathroom_price + extra_price + dry_cleaning_price)
        
        response_data = {
            "price": str(total_price),
            "breakdown": {
                "rooms_bathrooms": str(room_bathroom_price),
                "cleaning": str(cleaning_price),
                "extra_services": str(extra_price),
                "dry_cleaning": str(dry_cleaning_price),
            }
        }
        
        # Добавляем опциональные поля только если они есть
        if old_price:
            response_data["old_price"] = old_price
        
        if promo and promo.text:
            response_data["promo_text"] = promo.text
        
        return JsonResponse(response_data)
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        # Логируем полную ошибку для отладки
        print(f"API Error: {error_msg}")
        print(traceback.format_exc())
        return JsonResponse({
            "error": f"Ошибка расчёта: {error_msg}"
        }, status=500)


def get_services_api(request):
    """API endpoint для получения списка услуг"""
    extra_services = ExtraService.objects.filter(is_active=True).values(
        'id', 'name', 'price', 'price_type'
    )
    dry_cleaning_services = DryCleaningService.objects.filter(is_active=True).values(
        'id', 'name', 'price', 'unit'
    )
    
    return JsonResponse({
        "extra_services": list(extra_services),
        "dry_cleaning_services": list(dry_cleaning_services),
    })


def create_order_api(request):
    """API endpoint для создания заявки"""
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    import json
    from .models import Order
    from decimal import Decimal, InvalidOperation
    
    try:
        data = json.loads(request.body)
        
        # Валидация обязательных полей
        if not data.get('name') or not data.get('phone'):
            return JsonResponse({"error": "Имя и телефон обязательны"}, status=400)
        
        if not data.get('level') or not data.get('area'):
            return JsonResponse({"error": "Уровень уборки и площадь обязательны"}, status=400)
        
        # Валидация и парсинг данных
        try:
            area = Decimal(str(data.get('area', 0)))
            rooms = int(data.get('rooms', 0))
            bathrooms = int(data.get('bathrooms', 0))
            total_price = Decimal(str(data.get('total_price', 0)))
        except (ValueError, InvalidOperation, TypeError):
            return JsonResponse({"error": "Некорректные числовые значения"}, status=400)
        
        # Валидация уровня уборки
        valid_levels = ["basic", "general", "general_plus"]
        if data.get('level') not in valid_levels:
            return JsonResponse({"error": f"Некорректный уровень уборки"}, status=400)
        
        # Парсинг даты и времени (если есть)
        desired_date = None
        desired_time = None
        if data.get('desired_date'):
            try:
                from datetime import datetime
                desired_date = datetime.strptime(data.get('desired_date'), '%Y-%m-%d').date()
            except (ValueError, TypeError):
                pass
        
        if data.get('desired_time'):
            try:
                from datetime import datetime
                desired_time = datetime.strptime(data.get('desired_time'), '%H:%M').time()
            except (ValueError, TypeError):
                pass
        
        # Парсинг скидки
        applied_discount_percent = int(data.get('applied_discount_percent', 0))

        # Обработка дополнительных услуг
        extra_services_ids = data.get('extra_services') or []
        if not isinstance(extra_services_ids, list):
            extra_services_ids = []

        extra_services_text = None
        if extra_services_ids:
            services_qs = ExtraService.objects.filter(id__in=extra_services_ids)
            services_map = {service.id: service for service in services_qs}
            lines = []
            for raw_id in extra_services_ids:
                try:
                    service_id = int(raw_id)
                except (ValueError, TypeError):
                    continue
                service = services_map.get(service_id)
                if not service:
                    continue
                price_display = f"{service.price} Kč" if service.price_type == 'fixed' else f"{service.price} Kč/м²"
                lines.append(f"{service.name} — {price_display}")
            if lines:
                extra_services_text = "\n".join(lines)

        # Обработка объектов химчистки
        dry_cleaning_payload = data.get('dry_cleaning_items') or {}
        if not isinstance(dry_cleaning_payload, dict):
            dry_cleaning_payload = {}

        dry_cleaning_text = None
        if dry_cleaning_payload:
            dry_ids = []
            for raw_id in dry_cleaning_payload.keys():
                try:
                    dry_ids.append(int(raw_id))
                except (ValueError, TypeError):
                    continue

            services_qs = DryCleaningService.objects.filter(id__in=dry_ids)
            services_map = {service.id: service for service in services_qs}
            lines = []
            for raw_id, qty in dry_cleaning_payload.items():
                try:
                    service_id = int(raw_id)
                    quantity = Decimal(str(qty))
                except (ValueError, TypeError, InvalidOperation):
                    continue
                if quantity <= 0:
                    continue
                service = services_map.get(service_id)
                if not service:
                    continue
                unit_label = 'м²' if service.unit == 'm2' else 'шт'
                lines.append(f"{service.name} — {quantity} {unit_label}")
            if lines:
                dry_cleaning_text = "\n".join(lines)

        # Создание заявки
        order = Order.objects.create(
            name=data.get('name'),
            phone=data.get('phone'),
            email=data.get('email') or None,
            cleaning_level=data.get('level'),
            area=area,
            rooms=rooms,
            bathrooms=bathrooms,
            total_price=total_price,
            address=data.get('address') or None,
            desired_date=desired_date,
            desired_time=desired_time,
            applied_discount_percent=applied_discount_percent,
            comment=data.get('comment') or None,
            extra_services=extra_services_text,
            dry_cleaning_items=dry_cleaning_text,
            status='new'
        )
        
        # Формируем текст для отправки в Google Forms или WhatsApp
        order_text = format_order_for_external(order, data)
        
        # URL для отправки (можно настроить в админке или через переменные окружения)
        whatsapp_number = CompanyInfo.get_info().whatsapp
        if not whatsapp_number:
            whatsapp_number = "77077801708" # Номер основателя по умолчанию
        google_forms_url = ""  # Можно добавить в CompanyInfo
        
        # Отправка в Google Sheets (асинхронно, чтобы не блокировать ответ)
        def _append_to_sheet_async(order_id):
            try:
                from .models import Order as OrderModel
                from .google_sheets import append_to_google_sheet
                instance = OrderModel.objects.filter(id=order_id).first()
                if instance:
                    append_to_google_sheet(instance)
            except Exception as async_exc:
                print(f"Failed to append to Google Sheet async: {async_exc}")

        import threading
        threading.Thread(target=_append_to_sheet_async, args=(order.id,), daemon=True).start()

        return JsonResponse({
            "success": True,
            "message": "Заявка успешно создана",
            "order_id": order.id,
            "order_text": order_text,
            "whatsapp_url": f"https://wa.me/{whatsapp_number.replace('+', '').replace(' ', '').replace('-', '')}?text={order_text}" if whatsapp_number else None,
            "google_forms_url": google_forms_url
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "Некорректный JSON"}, status=400)
    except Exception as e:
        import traceback
        print(f"Error creating order: {e}")
        print(traceback.format_exc())
        return JsonResponse({"error": f"Ошибка создания заявки: {str(e)}"}, status=500)


def get_reviews_api(request):
    """API endpoint для получения списка отзывов"""
    reviews = Review.objects.filter(is_active=True).values(
        'id', 'name', 'text', 'rating', 'photo_url', 'date'
    )
    # Преобразуем date в строку
    reviews_list = []
    for review in reviews:
        review['date'] = review['date'].strftime('%Y-%m-%d') if review['date'] else None
        reviews_list.append(review)
    
    return JsonResponse(list(reviews_list), safe=False)


def get_advantages_api(request):
    """API endpoint для получения списка преимуществ"""
    advantages = Advantage.objects.filter(is_active=True).values(
        'id', 'title', 'description', 'icon'
    )
    return JsonResponse(list(advantages), safe=False)


def get_gallery_api(request):
    """API endpoint для получения галереи до/после"""
    gallery = GalleryItem.objects.filter(is_active=True).values(
        'id', 'before_image', 'after_image', 'caption'
    )
    return JsonResponse(list(gallery), safe=False)


def get_company_info_api(request):
    """API endpoint для получения информации о компании"""
    company = CompanyInfo.get_info()
    
    # Формируем ответ с социальными сетями
    data = {
        'phone': company.phone,
        'email': company.email,
        'address': company.address,
        'social_links': {
            'whatsapp': company.whatsapp or None,
            'telegram': company.telegram or None,
            'instagram': company.instagram or None,
            'facebook': company.facebook or None,
        },
    }
    
    if company.map_lat and company.map_lng:
        data['map_lat'] = float(company.map_lat)
        data['map_lng'] = float(company.map_lng)
    
    return JsonResponse(data)


def get_calendar_discounts_api(request):
    """API endpoint для получения скидок по датам для календаря"""
    from django.utils import timezone
    from datetime import timedelta
    from .models import DateDiscount
    
    today = timezone.now().date()
    end_date = today + timedelta(days=60)  # на 2 месяца вперёд
    
    discounts = DateDiscount.objects.filter(
        date__gte=today,
        date__lte=end_date,
        is_active=True
    ).order_by('date', '-discount_percent')  # Если на одну дату несколько скидок, берём максимальную
    
    # Создаём словарь для быстрого поиска: {'2026-01-10': 20, ...}
    # Если на одну дату несколько скидок, берём максимальную
    discount_map = {}
    for discount in discounts:
        date_str = discount.date.strftime('%Y-%m-%d')
        # Если уже есть скидка на эту дату, берём максимальную
        if date_str not in discount_map or discount.discount_percent > discount_map[date_str]:
            discount_map[date_str] = discount.discount_percent
    
    return JsonResponse(discount_map)


def get_cleaning_services_api(request):
    """API endpoint для получения описаний уровней уборки"""
    # Используем данные из CleaningPrice для формирования описаний
    services = []
    levels = ['basic', 'general', 'general_plus']
    
    for level in levels:
        prices = CleaningPrice.objects.filter(level=level, is_active=True).order_by('sort_order', 'area_from')
        if prices.exists():
            # Базовое описание на основе уровня
            descriptions = {
                'basic': {
                    'title': 'BASIC',
                    'description': 'Базовая уборка для регулярного поддержания чистоты',
                    'included_items': ['Влажная уборка полов', 'Протирка пыли', 'Чистка санузлов', 'Вынос мусора'],
                },
                'general': {
                    'title': 'GENERAL',
                    'description': 'Глубокая уборка с детальной обработкой всех поверхностей',
                    'included_items': ['Всё из BASIC', 'Мытьё окон', 'Чистка кухни', 'Пылесос мягкой мебели'],
                },
                'general_plus': {
                    'title': 'GENERAL PLUS',
                    'description': 'Премиум уборка с использованием профессиональных средств',
                    'included_items': ['Всё из GENERAL', 'Химчистка ковров', 'Полировка поверхностей', 'Ароматизация'],
                },
            }
            
            service_info = descriptions.get(level, {
                'title': level.upper(),
                'description': '',
                'included_items': [],
            })
            
            services.append({
                'id': len(services) + 1,
                'title': service_info['title'],
                'description': service_info['description'],
                'included_items': service_info['included_items'],
            })
    
    return JsonResponse(services, safe=False)


def format_order_for_external(order, data):
    """Форматирует заявку в текст для отправки в Google Forms или WhatsApp"""
    from .models import CompanyInfo
    from decimal import Decimal
    
    level_names = {
        'basic': 'BASIC',
        'general': 'GENERAL',
        'general_plus': 'GENERAL PLUS'
    }
    
    lines = [
        "🧹 НОВАЯ ЗАЯВКА НА УБОРКУ",
        "",
        f"👤 Имя: {order.name}",
        f"📞 Телефон: {order.phone}",
    ]
    
    if order.email:
        lines.append(f"📧 Email: {order.email}")
    
    lines.extend([
        "",
        "📋 ПАРАМЕТРЫ УБОРКИ:",
        f"   Уровень: {level_names.get(order.cleaning_level, order.cleaning_level)}",
        f"   Площадь: {order.area} м²",
        f"   Комнаты: {order.rooms}",
        f"   Туалеты: {order.bathrooms}",
    ])
    
    if order.desired_date:
        date_str = order.desired_date.strftime('%d.%m.%Y')
        lines.append(f"📅 Дата: {date_str}")
        if order.applied_discount_percent > 0:
            lines.append(f"   Скидка: -{order.applied_discount_percent}%")
    
    if order.desired_time:
        time_str = order.desired_time.strftime('%H:%M')
        lines.append(f"⏰ Время: {time_str}")
    
    lines.extend([
        "",
        f"💰 ИТОГОВАЯ ЦЕНА: {order.total_price} Kč",
    ])
    
    if order.applied_discount_percent > 0:
        # Вычисляем оригинальную цену
        original_price = order.total_price / (Decimal('1') - Decimal(str(order.applied_discount_percent)) / Decimal('100'))
        savings = original_price - order.total_price
        lines.append(f"   (Скидка: -{order.applied_discount_percent}%, экономия: {savings:.2f} Kč)")
    
    if order.address:
        lines.extend([
            "",
            f"📍 Адрес: {order.address}",
        ])
    
    if order.comment:
        lines.extend([
            "",
            f"💬 Комментарий: {order.comment}",
        ])
    
    lines.extend([
        "",
        f"🆔 ID заявки: #{order.id}",
        f"📅 Создано: {order.created_at.strftime('%d.%m.%Y %H:%M')}",
    ])
    
    return "\n".join(lines)


def get_cargo_services_api(request):
    """API endpoint для получения тарифов и опций грузоперевозок"""
    tariffs = CargoTariff.objects.filter(is_active=True).values(
        'id', 'name', 'price_per_hour', 'min_hours'
    )
    options = CargoOption.objects.filter(is_active=True).values(
        'id', 'name', 'price'
    )
    return JsonResponse({
        'tariffs': list(tariffs),
        'options': list(options),
    })


def get_shoe_cleaning_api(request):
    """API endpoint для получения услуг химчистки обуви"""
    services = ShoeCleaningService.objects.filter(is_active=True).values(
        'id', 'name', 'price_per_pair'
    )
    return JsonResponse({
        'services': list(services),
    })
