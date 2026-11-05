from django.conf import settings
from django.db import models
from django.db.models import Q

from restaurants.models import FoodItem, Restaurant


class FoodProductionLog(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='production_logs'
    )
    food_item = models.ForeignKey(
        FoodItem,
        on_delete=models.CASCADE,
        related_name='production_logs'
    )
    date = models.DateField()
    prepared_quantity = models.PositiveIntegerField()
    sold_quantity = models.PositiveIntegerField(default=0)
    wasted_quantity = models.PositiveIntegerField(default=0)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_production_logs'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'food_item__name']
        constraints = [
            models.UniqueConstraint(
                fields=['food_item', 'date'],
                name='unique_food_production_log_per_day'
            ),
            models.CheckConstraint(
                condition=Q(
                    prepared_quantity__gte=models.F('sold_quantity') + models.F('wasted_quantity')
                ),
                name='sold_and_wasted_not_above_prepared'
            )
        ]

    def __str__(self):
        return f'{self.food_item.name} production on {self.date}'
