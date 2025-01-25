from django.contrib import admin

from request.models import Request, MpesaTransfer, WithdrawMpesaPaymentTransaction

# Register your models here.
admin.site.register(Request)
admin.site.register(MpesaTransfer)
admin.site.register(WithdrawMpesaPaymentTransaction)