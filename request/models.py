from django.db import models
from django.utils.timezone import now

from appuser.models import AppUser
from celebservice.models import CelebService
from constants import STATE_CHOICES, PENDING, sender_password, sender_email, COMPANY_EMAIL
from models import ParentModel
from utils import sendMail


class Request(ParentModel):
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    companyamount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    clientamount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    client = models.ForeignKey(AppUser, default=None, on_delete=models.CASCADE, related_name='payments_as_client')
    celeb = models.ForeignKey(AppUser, default=None, on_delete=models.CASCADE, related_name='payments_as_celeb')
    celebservice = models.ForeignKey(CelebService, default=None, on_delete=models.CASCADE, related_name='payments')
    auto_date = models.DateTimeField(default=now)
    state = models.CharField(max_length=15, choices=STATE_CHOICES, default=PENDING)
    rescheduled_date = models.DateTimeField(null=True, blank=True)
    canceled_date = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(AppUser, on_delete=models.CASCADE, blank=True, null=True,
                                     related_name='cancellencations_as_user')
    customer_complete_celeb_remarks = models.TextField(null=True, blank=True, default="")
    duration = models.DurationField(null=True, blank=True)
    invoice_id = models.CharField(max_length=255, default="None")
    scheduled_date = models.DateTimeField(null=True, blank=True)
    refund_Request = models.BooleanField(default=False)
    refunded = models.BooleanField(default=False)
    refundedOn = models.CharField(max_length=255, blank=True, null=True)
    client_Reschedule_Request = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    complete_requested_by_celeb = models.BooleanField(default=False)
    customer_complete_request_accepted = models.BooleanField(default=False)
    customer_reject_remarks = models.CharField(max_length=255, null=True, blank=True)
    completed_date = models.DateField(blank=True, null=True)

    # location_name = models.CharField(max_length=255, null=True, blank=True, default="Pending Assignment By Celebrity")
    # location_latitude = models.FloatField(default=0.0, null=True, blank=True)
    # location_longitude = models.FloatField(default=0.0, null=True, blank=True)

    is_shout_out_video_recorded = models.BooleanField(default=False)
    shoutout_video = models.CharField(max_length=255, blank=True, null=True, default=None)
    shoutoutdescription = models.CharField(max_length=655, blank=True, null=True, default=None)

    withdraw_request = models.BooleanField(default=False)
    withdrawn = models.BooleanField(default=False)
    withdrawn_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Check if state is 'CANCEL' and update refund_Request to True
        if self.state == "CANCEL" or self.state == "CANCELED":
            self.refund_Request = True
            message = f"Refund request for {self.celebservice.serviceid.name} - {self.invoice_id} being processed"
            sendMail(sender_email, sender_password, self.client.email, "REFUND REQUEST", message)
            sendMail(sender_email, sender_password, self.celeb.email, "REFUND REQUEST", message)
            sendMail(sender_email, sender_password, COMPANY_EMAIL, "REFUND REQUEST", message)

        if self.state != "WITHDRAWN" and self.state != "WITHDRAWREQUEST" and self.complete_requested_by_celeb:
            self.state = "COMPLETED"

        if self.state != "WITHDRAWN" and self.shoutout_video and self.shoutout_video != "" and self.celebservice.serviceid.name == "SHOUTOUT":
            self.is_shout_out_video_recorded = True


        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.celeb.username} - {self.id}"

    class Meta:
        ordering = ['-updated_at']  # Order by most recent payments








class MpesaTransfer(models.Model):
    celeb = models.ForeignKey(AppUser, default=None, null=True, blank=True, on_delete=models.CASCADE, related_name='MpesaTransfer_Celeb')
    file_id = models.CharField(max_length=50, default="")
    device_id = models.CharField(max_length=50, null=True, blank=True, default="")
    tracking_id = models.CharField(max_length=100, unique=True, default="")
    batch_reference = models.CharField(max_length=100, null=True, blank=True, default="")
    status = models.CharField(max_length=100, default="")
    status_code = models.CharField(max_length=50, default="")
    nonce = models.CharField(max_length=50, default="")
    wallet_id = models.CharField(max_length=50, default="")
    wallet_label = models.CharField(max_length=100, default="")
    can_disburse = models.BooleanField(default=True)
    currency = models.CharField(max_length=10, default="")
    wallet_type = models.CharField(max_length=50, default="")
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    available_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    wallet_updated_at = models.DateTimeField()
    charge_estimate = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    total_amount_estimate = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    transactions_count = models.PositiveIntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return self.tracking_id




class WithdrawMpesaPaymentTransaction(models.Model):
    celeb = models.ForeignKey(AppUser, default=None, null=True, blank=True, on_delete=models.CASCADE, related_name='WithdrawMpesaPaymentTransaction_Celeb')
    transfer = models.ForeignKey(MpesaTransfer, on_delete=models.CASCADE, related_name="transactions")
    status = models.CharField(max_length=50, default="")
    status_code = models.CharField(max_length=50, default="")
    request_reference_id = models.CharField(max_length=100, default="")
    name = models.CharField(max_length=100, default="")
    account = models.CharField(max_length=20, default="")
    id_number = models.CharField(max_length=50, null=True, blank=True, default="")
    bank_code = models.CharField(max_length=50, null=True, blank=True, default="")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    narrative = models.TextField(null=True, blank=True, default="")

    def __str__(self):
        return self.request_reference_id
