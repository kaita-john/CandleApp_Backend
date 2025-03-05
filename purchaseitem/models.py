from django.db import models
from django.db.models import Sum

from item.models import Item


class PurchaseItem(models.Model):
    item = models.ForeignKey(Item, default=None, null=True, on_delete=models.CASCADE, related_name="purchaseitems")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=True)

    def save(self, *args, **kwargs):
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.total}" if self.item else ""



