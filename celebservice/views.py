# Create your views here.
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from appuser.models import AppUser
from service.models import Service
from utils import SchoolIdMixin, UUID_from_PrimaryKey, IsAdminOrSuperUser, DefaultMixin
from .models import CelebService
from .serializers import CelebServiceSerializer


class CelebServiceCreateView(SchoolIdMixin, generics.CreateAPIView):
    serializer_class = CelebServiceSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serviceid = request.data.get('serviceid')
        celebid = request.data.get('celebid')

        if serializer.is_valid():
            if not Service.objects.filter(id=serviceid).exists():
                return Response({'detail': f"Invalid Service Id"}, status=status.HTTP_400_BAD_REQUEST)
            if not AppUser.objects.filter(id=celebid).exists():
                return Response({'detail': f"Invalid Celeb Id"}, status=status.HTTP_400_BAD_REQUEST)
            self.perform_create(serializer)
            return Response({'detail': 'CelebService created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CelebServiceListView(SchoolIdMixin, DefaultMixin, generics.ListAPIView):
    serializer_class = CelebServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CelebService.objects.all()
        celebid = self.request.query_params.get('celebid', None)
        if celebid and celebid != "" and celebid != "null":
            queryset = queryset.filter(celebid=celebid)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return JsonResponse([], status=200, safe=False)
        serializer = self.get_serializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)


class CelebServiceDetailView(SchoolIdMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = CelebService.objects.all()
    serializer_class = CelebServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        primarykey = self.kwargs['pk']
        try:
            id = UUID_from_PrimaryKey(primarykey)
            return CelebService.objects.get(id=id)
        except (ValueError, CelebService.DoesNotExist):
            raise NotFound({'detail': 'Record Not Found'})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({'detail': 'CelebService updated successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': 'Record deleted successfully'}, status=status.HTTP_200_OK)


class CelebServiceDeleteAllObjects(SchoolIdMixin, APIView):

    def delete(self, request, *args, **kwargs):
        deleted_count, _ = CelebService.objects.all().delete()
        return Response({'detail': f"{deleted_count} CelebService objects deleted successfully."},
                        status=status.HTTP_200_OK)





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import CelebService, Service, AppUser

class CelebServiceUpdateOrCreate(APIView):
    def post(self, request, *args, **kwargs):
        celebid = request.data.get("celebid")
        request_type = request.data.get("request_type")
        amount = request.data.get("amount")

        # Validate inputs
        if not all([celebid, request_type, amount]):
            return Response({"details": "celebid, request_type, and amount are required."},status=status.HTTP_400_BAD_REQUEST)

        try:
            celeb = get_object_or_404(AppUser, id=celebid)
            service = Service.objects.filter(name=request_type).first()
            if not service:
                return Response({"details": f"Service type '{request_type}' does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            celeb_service, created = CelebService.objects.update_or_create(celebid=celeb,serviceid=service,defaults={"amount": int(amount)})
            status_message = "created" if created else "updated"
            return Response({
                    "details": f"Service {status_message} successfully.",
                    "service": f"{celeb_service.serviceid.name} - {celeb_service.celebid.username}",
                    "amount": celeb_service.amount
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response( {"details": f"An unexpected error occurred: {str(e)}"},  status=status.HTTP_500_INTERNAL_SERVER_ERROR )

