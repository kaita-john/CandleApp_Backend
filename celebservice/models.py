from django.db import models

from appuser.models import AppUser
from models import ParentModel
from service.models import Service


class CelebService(ParentModel):
    celebid = models.ForeignKey(AppUser, default=None, null=True, on_delete=models.CASCADE, related_name="celebservices")
    serviceid = models.ForeignKey(Service, default=None, null=True, on_delete=models.CASCADE, related_name="celebservices")
    amount = models.IntegerField(blank=True, null=True, default=0)
    def __str__(self):
        return f"{self.serviceid.name} - {self.celebid.username}"
