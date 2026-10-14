from django.urls import path
from . import views

app_name = 'rental_app'

urlpatterns = [
    path('', views.equipment_list, name='equipment_list'),
    path('scan/', views.ai_scan, name='ai_scan'),
    path('book/<int:equipment_id>/', views.book_rental, name='book_rental'),
    path('return/<int:rental_id>/', views.return_equipment, name='return_equipment'),
    path('history/', views.rental_history, name='rental_history'),
]
