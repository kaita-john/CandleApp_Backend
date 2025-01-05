from rest_framework import serializers

from appuser.serializers import AppUserSerializer
from mpesainvoices.models import MpesaInvoice
from service.serializers import ServiceSerializer


class MpesaInvoiceSerializer(serializers.ModelSerializer):
    celebid_details = AppUserSerializer(source='celebid', required=False, read_only=True)
    serviceid_details = ServiceSerializer(source='serviceid', required=False, read_only=True)
    class Meta:
        model = MpesaInvoice
        fields = '__all__'
