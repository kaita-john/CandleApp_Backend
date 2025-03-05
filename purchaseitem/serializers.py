from rest_framework import serializers

from item.serializers import ItemSerializer
from .models import PurchaseItem


class PurchaseItemSerializer(serializers.ModelSerializer):
    item_details = ItemSerializer(source='item', required=False, read_only=True)
    class Meta:
        model = PurchaseItem
        fields = '__all__'
        read_only_fields = ['total']
