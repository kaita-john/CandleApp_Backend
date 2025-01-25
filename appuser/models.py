import uuid

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from appuser.managers import CustomUserManager
from constants import GENDER_CHOICES, COMPANYID
from utils import BaseUserModel


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)



class AppUser(BaseUserModel, AbstractBaseUser, PermissionsMixin):
    id= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_staff = models.BooleanField(default=False)
    is_agent = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_celeb = models.BooleanField(default=True)

    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    confirmpassword = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=6,choices=GENDER_CHOICES,default='MALE')
    location = models.CharField(max_length=255, blank=True, null=True)
    roles = models.ManyToManyField(Group, related_name='users', blank=True)

    tagline = models.CharField(max_length=255, blank=True, null=True, default = "")
    biotext = models.CharField(max_length=255, blank=True, null=True, default = "")
    stagename = models.CharField(max_length=255, blank=True, null=True, default = "")
    image = models.CharField(max_length=255, blank=True, null=True, default = "")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.username or str(self.id)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def save(self, *args, **kwargs):
        is_celeb = kwargs.pop("is_celeb", None)
        super().save(*args, **kwargs)

        if is_celeb:
            from appuser.views import SendPushNotificationView
            print(f"It is a celebrity")
            celeb_group = Group.objects.get_or_create(name="CELEB")
            self.roles.add(celeb_group)
            self.groups.add(celeb_group)
            super().save(*args, **kwargs)

    class Meta:
        ordering = ["-date_created"]




