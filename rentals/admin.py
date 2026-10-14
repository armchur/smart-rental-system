from django.contrib import admin
from .models import EquipmentCategory, Equipment, Customer, Rental, RecognitionLog


@admin.register(EquipmentCategory)
class EquipmentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'serial_number', 'category', 'daily_rate', 'status', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('name', 'serial_number')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'id_card_number', 'created_at')
    search_fields = ('full_name', 'phone', 'id_card_number')


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'equipment', 'start_date', 'expected_return_date', 'status', 'total_amount')
    list_filter = ('status', 'start_date')
    search_fields = ('customer__full_name', 'equipment__name')


@admin.register(RecognitionLog)
class RecognitionLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'predicted_class', 'confidence', 'accepted', 'scanned_at')
    list_filter = ('accepted', 'predicted_class')
    readonly_fields = ('predicted_class', 'confidence', 'accepted', 'top3_json', 'scanned_at')
