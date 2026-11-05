from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import FoodProductionLog


@admin.register(FoodProductionLog)
class FoodProductionLogAdmin(admin.ModelAdmin):
    list_display = (
        'food_item',
        'restaurant',
        'date',
        'prepared_quantity',
        'sold_quantity',
        'wasted_quantity',
        'recorded_by',
    )
    list_filter = ('date', 'restaurant')
    search_fields = ('food_item__name', 'restaurant__name')
