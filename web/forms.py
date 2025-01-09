from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db import models
from appuser.models import AppUser

class AppUserBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None

class AppUserForm(forms.ModelForm):
    class Meta:
        model = AppUser
        fields = "__all__"


class GlobalSettingsModel(models.Model):
    id = models.IntegerField(primary_key=True)
    minimum_Student_Token_Balance_To_Make_Calls = models.FloatField(max_length=255, default=0.0, blank=True, null=True)
    minimum_Overall_School_Minute_Balance_To_Allow_Calls = models.FloatField(max_length=255, default=0.0, blank=True, null=True)
    minimum_Device_Token_Balance_To_Allow_Calls = models.FloatField(max_length=255, default=0.0, blank=True, null=True)
    def __str__(self):
        return f"{self.minimum_Student_Token_Balance_To_Make_Calls}"


class GlobalSettingsForm(forms.ModelForm):
    class Meta:
        model = GlobalSettingsModel
        exclude = ['id']



class LoginModel(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    def __str__(self):
        return f"${self.username}-{self.password}"
class LoginForm(forms.ModelForm):
    class Meta:
        model = LoginModel
        fields = "__all__"

