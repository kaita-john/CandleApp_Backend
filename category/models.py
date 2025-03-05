from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, default="")

    def __str__(self):
        return f"{self.name}"