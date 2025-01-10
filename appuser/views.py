import requests
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from rest_framework import generics, status
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from appuser.models import AppUser  # Import your custom user model
from appuser.serializers import AppUserSerializer, PushNotificationSerializer, FeedbackSerializer, PasswordSerializer
from constants import ONESIGNAL_API_KEY, ONESIGNAL_APP_ID, sender_email, sender_password, COMPANY_EMAIL
from utils import SchoolIdMixin, UUID_from_PrimaryKey, sendMail


@never_cache
def deleteAccount(request):
    if request.method == "POST":
        try:
            email = request.POST.get("email", "").strip()
            password = request.POST.get("password", "").strip()

            if not email or not password:
                messages.error(request, _("Email address and password are required!"))
                return redirect("deleteaccountpage")

            try:
                user = AppUser.objects.get(email=email)
                if user.check_password(password):
                    user.delete()
                    messages.success(request, _("Your account has been deleted successfully."))
                    return redirect("deleteaccountpage")
                else:
                    messages.error(request, _("Incorrect password. Please try again."))
                    return redirect("deleteaccountpage")

            except AppUser.DoesNotExist:
                messages.error(request, _("No user found with that email address."))
                return redirect("deleteaccountpage")
            except Exception as deletion_exception:
                messages.error(request, _(f"An error occurred while deleting the account: {deletion_exception}"))
                return redirect("deleteaccountpage")

        except Exception as exception:
            messages.error(request, _(f"An unexpected error occurred: {exception}"))
            return redirect("deleteaccountpage")

    # Render the delete account form if GET request
    return render(request, "login.html", {"summary": []})


@never_cache
def childSafety(request):
    return render(request, "child-safety.html", {"summary": []})


class AppUserCreateView(generics.CreateAPIView):
    serializer_class = AppUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            response_data = self.perform_create(serializer)
            return Response({'details': 'User saved successfully'}, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response({'details': e.detail}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        email = serializer.validated_data['email']
        qs = AppUser.objects.filter(username=email)
        if qs.exists():
            raise serializers.ValidationError({'details': 'User already exists'})

        if serializer.is_valid():
            print("Serializer is valid. Data:")
            print(serializer.validated_data)
            user = serializer.save()

            # Check if the user is a celebrity and assign group
            is_celeb = serializer.validated_data.get("is_celeb", False)
            if is_celeb:
                print(f"It is a celebrity")
                user.is_admin = True
                celeb_group, created = Group.objects.get_or_create(name="CELEB")  # Get or create CELEB group
                user.roles.add(celeb_group)
                user.groups.add(celeb_group)
                user.save()
            return user

        else:
            print("Serializer is not valid. Errors:")
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppUserListView(SchoolIdMixin, generics.ListAPIView):
    serializer_class = AppUserSerializer
    # permission_classes = [IsAuthenticated]
    pagination_class = None  # Disable pagination for this view

    def get_queryset(self):
        queryset = AppUser.objects.all()
        role_name = self.request.query_params.get('role_name')  # Get the 'role_name' from query parameters
        if role_name:
            print("AM HERE")
            queryset = queryset.filter(groups__name=role_name, is_admin=False)  # Filter by the role name
        else:
            print("AM NOT HERE")
        return queryset


class AppUserDetailView(SchoolIdMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = AppUser.objects.all()
    serializer_class = AppUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        primarykey = self.kwargs['pk']
        try:
            id = UUID_from_PrimaryKey(primarykey)
            return AppUser.objects.get(id=id)
        except (ValueError, AppUser.DoesNotExist):
            raise NotFound({'details': 'Record Not Found'})

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({'details': 'User updated successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'details': 'Record deleted successfully'}, status=status.HTTP_200_OK)


class FineAppUserListView(SchoolIdMixin, generics.ListAPIView):
    serializer_class = AppUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        school_id = self.check_school_id(self.request)
        if not school_id:
            return JsonResponse({'details': 'Invalid school in token'}, status=401)

        user_id = self.request.user.id
        queryset = AppUser.objects.filter(school_id=school_id, id=user_id)
        return queryset


class RoleListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        if user_id and user_id != "zx":
            user = get_object_or_404(AppUser, id=user_id)
        else:
            user = request.user

        roles = user.roles.all() if user else []
        role_data = [{'name': role.name, 'id': role.id} for role in roles]
        return Response(role_data)


class SendPushNotificationView(generics.CreateAPIView):
    serializer_class = PushNotificationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        external_id = serializer.validated_data['external_id']
        message = serializer.validated_data['message']
        response = self.send_push_notification_by_external_id(external_id, message)

        if 'error' in response:
            return Response({'error': response['error']}, status=status.HTTP_400_BAD_REQUEST)
        return Response(response, status=status.HTTP_200_OK)

    def send_push_notification_by_external_id(self, external_id, message):
        url = 'https://onesignal.com/api/v1/notifications'
        headers = {
            'Authorization': f'Basic {ONESIGNAL_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            "app_id": ONESIGNAL_APP_ID,
            "include_external_user_ids": [external_id],
            "contents": {"en": message},
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': response.text}


class FeedbackView(generics.CreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            # Validate the request data using the serializer
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Extracting data from the serializer
            feedback = serializer.validated_data['feedback']
            mobile = serializer.validated_data['mobile']
            userid = serializer.validated_data['userid']

            # Create the feedback message
            message = f"Feedback: {feedback}\nMobile: {mobile}\nUser ID: {userid}"

            # Send the email (assumes sendMail is defined elsewhere)
            sendMail(sender_email, sender_password, COMPANY_EMAIL, "FEEDBACK", message)

            # Return a success response
            return Response(
                {"details": "Thank you for your feedback!"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            # Log the exception (replace with proper logging)
            print(f"Error occurred: {e}")  # For debugging; use a logging library in production

            # Return an error response
            return Response(
                {"error": "An error occurred while submitting feedback. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PasswordUPdateView(generics.CreateAPIView):
    serializer_class = PasswordSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        try:
            user = AppUser.objects.get(username=email)
        except AppUser.DoesNotExist:
            return Response({"error": "No user found with the provided email."}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(password)
        user.save()
        return Response({"details": "Password updated successfully. Login with your new password"},status=status.HTTP_200_OK)
