from rest_framework import serializers

from appuser.serializers import AppUserSerializer
from celebservice.models import CelebService
from service.serializers import ServiceSerializer


class CelebServiceSerializer(serializers.ModelSerializer):
    celebid_details = AppUserSerializer(source='celebid', required=False, read_only=True)
    serviceid_details = ServiceSerializer(source='serviceid', required=False, read_only=True)
    class Meta:
        model = CelebService
        fields = '__all__'
