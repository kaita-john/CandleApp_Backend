from django.db import models

from appuser.models import AppUser
from celebservice.models import CelebService
from models import ParentModel


class MpesaInvoice(ParentModel):
    celebservice = models.ForeignKey(CelebService, default=None, null=True, on_delete=models.CASCADE, related_name="mpesainvoices")
    client = models.ForeignKey(AppUser, default=None, null=True, on_delete=models.CASCADE, related_name="mpesainvoices")
    invoice = models.CharField(max_length=255, default="None")
    def __str__(self):
        return f"Client {self.client.id} - {self.celebservice.serviceid.name}"
