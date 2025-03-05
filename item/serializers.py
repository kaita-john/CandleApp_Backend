from rest_framework import serializers

from category.serializers import CategorySerializer
from item.models import Item
from itemimages.serializers import ItemImageSerializer


class ItemSerializer(serializers.ModelSerializer):
    itemimages = ItemImageSerializer(many=True, read_only=True)
    category_details = CategorySerializer(source='category', required=False, read_only=True)

    class Meta:
        model = Item
        fields = '__all__'