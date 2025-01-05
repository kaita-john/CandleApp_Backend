from django.contrib.auth.models import Group
from rest_framework import serializers

from appuser.models import AppUser


class FetchRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class AppUserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=False)
    confirmpassword = serializers.CharField(write_only=True, required=False)
    school_id = serializers.UUIDField(required=False)
    roles = FetchRoleSerializer(source='groups', many=True, required=False)

    class Meta:
        model = AppUser
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'confirmpassword': {'write_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        validated_data['password'] = password
        user = AppUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)

        instance.save()
        return instance



class PushNotificationSerializer(serializers.Serializer):
    external_id = serializers.CharField(required=True)
    message = serializers.CharField(required=True)