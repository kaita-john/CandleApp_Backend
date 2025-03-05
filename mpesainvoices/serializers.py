from rest_framework import serializers

from mpesainvoices.models import MpesaInvoice


class MpesaInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaInvoice
        fields = '__all__'
