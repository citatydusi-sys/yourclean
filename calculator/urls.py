from django.urls import path
from . import views

app_name = 'calculator'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('calculator/', views.calculator_view, name='calculator'),
    path('api/price/', views.calculate_price_api, name='price_api'),
    path('api/services/', views.get_services_api, name='services_api'),
    path('api/orders/', views.create_order_api, name='orders_api'),
    path('api/reviews/', views.get_reviews_api, name='reviews_api'),
    path('api/advantages/', views.get_advantages_api, name='advantages_api'),
    path('api/gallery/', views.get_gallery_api, name='gallery_api'),
    path('api/company/', views.get_company_info_api, name='company_info_api'),
    path('api/cleaning-services/', views.get_cleaning_services_api, name='cleaning_services_api'),
    path('api/calendar-discounts/', views.get_calendar_discounts_api, name='calendar_discounts_api'),
]

