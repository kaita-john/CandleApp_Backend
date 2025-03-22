from django.db import models

from category.models import Category


class Item(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True,  default="")
    mainimage = models.CharField(max_length=255, blank=True, null=True, default="")
    inStock = models.BooleanField(default=True)
    category = models.ForeignKey(Category, default=None, null=True, on_delete=models.CASCADE, related_name="items")

    def __str__(self):
        return self.name





class StockNotification(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    product_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.product_name}"