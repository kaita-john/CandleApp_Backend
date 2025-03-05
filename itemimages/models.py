from django.db import models

from item.models import Item


class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='itemimages')  # Use related_name
    image = models.CharField(max_length=255, blank=True, null=True, default="")

    def __str__(self):
        return f"Image for {self.item.name}"  # Clearer representation