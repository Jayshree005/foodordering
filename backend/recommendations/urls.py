from django.urls import path

from .views import (
    demand_forecast,
    dish_recommendations,
    production_logs,
    waste_forecast,
)

urlpatterns = [
    path('dishes/', dish_recommendations, name='dish-recommendations'),
    path('admin/demand-forecast/', demand_forecast, name='demand-forecast'),
    path('admin/production-logs/', production_logs, name='production-logs'),
    path('admin/waste-forecast/', waste_forecast, name='waste-forecast'),
]
