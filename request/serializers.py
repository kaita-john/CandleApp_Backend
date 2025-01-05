from rest_framework import serializers

from appuser.serializers import AppUserSerializer
from celebservice.serializers import CelebServiceSerializer
from request.models import Request


class RequestSerializer(serializers.ModelSerializer):
    client_Object = AppUserSerializer(source='client', required=False, read_only=True)
    celeb_Object = AppUserSerializer(source='celeb', required=False, read_only=True)
    celebservice_Object = CelebServiceSerializer(source='celebservice', required=False, read_only=True)
    class Meta:
        model = Request
        fields = '__all__'
