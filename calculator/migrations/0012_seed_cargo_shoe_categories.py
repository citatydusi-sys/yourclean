"""
Data migration to seed initial Cargo, Shoe Cleaning, and ServiceCategory data.
"""
from django.db import migrations


def seed_data(apps, schema_editor):
    CargoTariff = apps.get_model('calculator', 'CargoTariff')
    CargoOption = apps.get_model('calculator', 'CargoOption')
    ShoeCleaningService = apps.get_model('calculator', 'ShoeCleaningService')
    ServiceCategory = apps.get_model('calculator', 'ServiceCategory')

    # Cargo tariffs (set all translation fields)
    CargoTariff.objects.bulk_create([
        CargoTariff(name='Машина с водителем', name_ru='Машина с водителем', name_en='Van with driver', name_cs='Auto s řidičem', price_per_hour=750, min_hours=1.5, sort_order=1),
        CargoTariff(name='Машина + 1 грузчик', name_ru='Машина + 1 грузчик', name_en='Van + 1 mover', name_cs='Auto + 1 stěhovák', price_per_hour=1100, min_hours=1.5, sort_order=2),
        CargoTariff(name='Машина + 2 грузчика', name_ru='Машина + 2 грузчика', name_en='Van + 2 movers', name_cs='Auto + 2 stěhováci', price_per_hour=1350, min_hours=1.0, sort_order=3),
        CargoTariff(name='Машина + 3 грузчика', name_ru='Машина + 3 грузчика', name_en='Van + 3 movers', name_cs='Auto + 3 stěhováci', price_per_hour=1600, min_hours=1.0, sort_order=4),
    ])

    # Cargo options
    CargoOption.objects.bulk_create([
        CargoOption(name='Монтаж мебели', name_ru='Монтаж мебели', name_en='Furniture assembly', name_cs='Montáž nábytku', price=650, sort_order=1),
        CargoOption(name='Упаковка', name_ru='Упаковка', name_en='Packing', name_cs='Balení', price=400, sort_order=2),
    ])

    # Shoe cleaning services
    ShoeCleaningService.objects.bulk_create([
        ShoeCleaningService(name='Кроссовки/Кеды', name_ru='Кроссовки/Кеды', name_en='Sneakers/Trainers', name_cs='Tenisky/Kecky', price_per_pair=500, sort_order=1),
        ShoeCleaningService(name='Кожаная/Замшевая обувь', name_ru='Кожаная/Замшевая обувь', name_en='Leather/Suede shoes', name_cs='Kožená/Semišová obuv', price_per_pair=600, sort_order=2),
    ])

    # Service categories (cards for Step 2)
    categories = [
        {
            'slug': 'cleaning',
            'title': 'УБОРКА ПОМЕЩЕНИЙ', 'title_ru': 'УБОРКА ПОМЕЩЕНИЙ', 'title_en': 'CLEANING', 'title_cs': 'ÚKLID',
            'description': 'Профессиональный клининг, от генеральной до поддерживающей. Ваш дом будет сиять.',
            'description_ru': 'Профессиональный клининг, от генеральной до поддерживающей. Ваш дом будет сиять.',
            'description_en': 'Professional cleaning, from deep to maintenance. Your home will shine.',
            'description_cs': 'Profesionální úklid, od generálního po udržovací. Váš domov bude zářit.',
            'sort_order': 1,
        },
        {
            'slug': 'drycleaning',
            'title': 'ПРОФЕССИОНАЛЬНАЯ ХИМЧИСТКА', 'title_ru': 'ПРОФЕССИОНАЛЬНАЯ ХИМЧИСТКА', 'title_en': 'DRY CLEANING', 'title_cs': 'PROFESIONÁLNÍ ČIŠTĚNÍ',
            'description': 'Бережное восстановление мебели, ковров и матрасов. Глубокое очищение и свежесть.',
            'description_ru': 'Бережное восстановление мебели, ковров и матрасов. Глубокое очищение и свежесть.',
            'description_en': 'Careful restoration of furniture, carpets and mattresses. Deep cleaning and freshness.',
            'description_cs': 'Šetrná obnova nábytku, koberců a matrací. Hluboké čištění a svěžest.',
            'sort_order': 2,
        },
        {
            'slug': 'cargo',
            'title': 'ГРУЗОПЕРЕВОЗКИ', 'title_ru': 'ГРУЗОПЕРЕВОЗКИ', 'title_en': 'CARGO TRANSPORT', 'title_cs': 'STĚHOVÁNÍ',
            'description': 'Машина с водителем и грузчиками. Монтаж и упаковка мебели.',
            'description_ru': 'Машина с водителем и грузчиками. Монтаж и упаковка мебели.',
            'description_en': 'Van with driver and movers. Furniture assembly and packing.',
            'description_cs': 'Auto s řidičem a stěhováky. Montáž a balení nábytku.',
            'sort_order': 3,
        },
        {
            'slug': 'shoe_cleaning',
            'title': 'ХИМЧИСТКА ОБУВИ', 'title_ru': 'ХИМЧИСТКА ОБУВИ', 'title_en': 'SHOE CLEANING', 'title_cs': 'ČIŠTĚNÍ OBUVI',
            'description': 'Кроссовки, кожа, замша — вернём обуви первозданный вид.',
            'description_ru': 'Кроссовки, кожа, замша — вернём обуви первозданный вид.',
            'description_en': 'Sneakers, leather, suede — we restore your shoes to their original look.',
            'description_cs': 'Tenisky, kůže, semiš — vrátíme obuvi původní vzhled.',
            'sort_order': 4,
        },
    ]
    for cat in categories:
        ServiceCategory.objects.create(**cat)


def reverse_data(apps, schema_editor):
    CargoTariff = apps.get_model('calculator', 'CargoTariff')
    CargoOption = apps.get_model('calculator', 'CargoOption')
    ShoeCleaningService = apps.get_model('calculator', 'ShoeCleaningService')
    ServiceCategory = apps.get_model('calculator', 'ServiceCategory')

    CargoTariff.objects.all().delete()
    CargoOption.objects.all().delete()
    ShoeCleaningService.objects.all().delete()
    ServiceCategory.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0011_cargooption_cargotariff_servicecategory_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_data, reverse_data),
    ]
