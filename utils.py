import os
import random
import smtplib
import string
import time
import uuid
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import jwt
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from rest_framework import permissions, status
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from app import settings
from app.settings import SIMPLE_JWT


class BaseUserModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_deleted = models.DateTimeField(blank=True, null=True)
    date_joined = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True


class SchoolIdMixin:
    def check_school_id(self, request):
        auth_header = get_authorization_header(request).decode('utf-8')
        if not auth_header or 'Bearer ' not in auth_header:
            raise ValidationError({'detail': 'No valid Authorization header'})

        token = auth_header.split(' ')[1]

        try:
            # Decode the JWT token
            decoded_token = jwt.decode(token, SIMPLE_JWT['SIGNING_KEY'], algorithms=[SIMPLE_JWT['ALGORITHM']])
            school_id = decoded_token.get('school_id')

            # Check if the school_id is valid (you may replace this with your validation logic)
            if not is_valid_school_id(school_id):
                raise ValidationError({'detail': 'Invalid school_id'})

            # Do something with the school_id
            return school_id
        except jwt.ExpiredSignatureError:
            raise ValidationError({'detail': 'Token has expired'})
        except jwt.InvalidTokenError:
            raise ValidationError({'detail': 'Invalid token'})


def is_valid_school_id(school_id):
    return True


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.roles.filter(name='ADMIN').exists()


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.roles.filter(name='SUPERUSER').exists()


class IsAdminOrSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.is_admin or IsAdminUser().has_permission(request,
                                                                                       view) or IsSuperUser().has_permission(
            request, view))


def fetchAllRoles():
    userroles = []
    query_set = Group.objects.all()
    if query_set.count() >= 1:
        for groups in query_set:
            userroles.append(groups)
        return userroles
    else:
        return userroles


def fetchusergroups(userid):
    userroles = []
    query_set = Group.objects.filter(user=userid)
    if query_set.count() >= 1:
        for groups in query_set:
            userroles.append(groups.name)
        return userroles
    else:
        return userroles


# def sendMail(sender_email, sender_password, receiver_email, subject, usermessage):
#     try:
#         message = 'Subject: {}\n\n{}'.format(subject, usermessage)
#         server = smtplib.SMTP('smtp.gmail.com', 587)
#         server.starttls()
#         server.login(sender_email, sender_password)
#         server.sendmail(sender_email, receiver_email, message)
#     except Exception as ex:
#         raise ValidationError({'detail': str(ex)})


def sendMail(sender_email, sender_password, receiver_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject

        # Add UTF-8 encoded message
        msg.attach(MIMEText(body, "plain", "utf-8"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()

    except Exception as ex:
        print("Email sending failed:", ex)


def generate_unique_code(prefix="INV"):
    timestamp = int(time.time())
    random_component = uuid.uuid4().hex[:6]
    unique_code = f"{prefix.upper()}{timestamp}{random_component}"
    return unique_code


def UUID_from_PrimaryKey(primarykey):
    id = uuid.UUID(primarykey)
    return id


def file_upload(instance, filename):
    ext = filename.split(".")[-1]
    now = datetime.now()

    if len(str(abs(now.month))) > 1:
        month = str(now.month)
    else:
        month = str(now.month).zfill(2)

    if len(str(abs(now.day))) > 1:
        day = str(now.day)
    else:
        day = str(now.day).zfill(2)

    if len(str(abs(now.hour))) > 1:
        hour = str(now.hour)
    else:
        hour = str(now.hour).zfill(2)

    # upload_to = f"{str(now.year)}/{month}/{day}/{hour}"
    upload_to = f"files"
    if instance.pk:
        filename = "{}.{}".format(instance.pk, ext)
    else:
        filename = "{}.{}".format(uuid.uuid4().hex, ext)
    return os.path.join(upload_to, filename)


def currentTerm(school_id):
    try:
        return Term.objects.get(is_current=True, school_id=school_id)
    except Term.DoesNotExist:
        return None


def check_if_object_exists(Model, obj_id):
    try:
        instance = Model.objects.get(id=obj_id)
        return True
    except ObjectDoesNotExist:
        return Response({'detail': f"{obj_id} is not a valid uuid"}, status=status.HTTP_400_BAD_REQUEST)


class DefaultMixin:
    def check_defaults(self, request, school_id):
        getcurrentTerm = currentTerm(school_id)

        if not getcurrentTerm:
            raise ValidationError({'detail': 'Current Term not set for this school!'})


def generate_random_password(self):
    char_set = string.ascii_letters + string.digits
    if settings.DEBUG:
        return ''.join(random.choices(char_set, k=8))
    return ''.join(random.choices(char_set + string.punctuation, k=12))
