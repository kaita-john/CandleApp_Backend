from datetime import date

from django.db import models

from purchaseitem.models import PurchaseItem


class Purchase(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True, default="")
    email = models.EmailField(null=True, blank=True)
    mobile = models.CharField(max_length=20, null=True, blank=True, default="")
    round = models.CharField(max_length=20, null=True, blank=True, default="")
    location = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=True)
    purchaseitems = models.ManyToManyField(PurchaseItem, related_name="purchases")
    dated = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.total_price}"
