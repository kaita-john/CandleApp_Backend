from rest_framework import serializers

from .models import MakeYourCandle


class MakeYourCandleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MakeYourCandle
        fields = '__all__'
    def to_internal_value(self, data):
        # Convert the 'purpose' list into a comma-separated string
        if 'purpose' in data and isinstance(data['purpose'], list):
            data['purpose'] = ', '.join(data['purpose'])
        return super().to_internal_value(data)