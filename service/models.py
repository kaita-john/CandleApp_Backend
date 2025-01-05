from django.db import models

from models import ParentModel


class Service(ParentModel):
    name = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.name} - {self.id}"
