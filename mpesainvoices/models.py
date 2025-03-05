from django.db import models

from models import ParentModel


class MpesaInvoice(ParentModel):
    invoice = models.CharField(max_length=255, default="None")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.invoice}"
