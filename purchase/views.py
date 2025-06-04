# Create your views here.
import json

from django.http import JsonResponse
from intasend import APIService
from intasend.exceptions import IntaSendBadRequest
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from appuser.models import AppUser
from constants import token, publishable_key
from mpesainvoices.models import MpesaInvoice
from utils import SchoolIdMixin, UUID_from_PrimaryKey, DefaultMixin
from .models import Purchase
from .serializers import PurchaseSerializer


class PurchaseCreateView(SchoolIdMixin, generics.CreateAPIView):
    serializer_class = PurchaseSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({'detail': 'Purchase created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PurchaseListView(SchoolIdMixin, DefaultMixin, generics.ListAPIView):
    serializer_class = PurchaseSerializer
    def get_queryset(self):
        queryset = Purchase.objects.all()
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


class PurchaseDetailView(SchoolIdMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    # permission_classes = [IsAuthenticated]

    def get_object(self):
        primarykey = self.kwargs['pk']
        try:
            return Purchase.objects.get(id=primarykey)
        except (ValueError, Purchase.DoesNotExist):
            raise NotFound({'detail': 'Record Not Found'})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({'detail': 'Purchase updated successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': 'Record deleted successfully'}, status=status.HTTP_200_OK)



class PurchaseDeleteAllObjects(SchoolIdMixin, APIView):
    def delete(self, request, *args, **kwargs):
        deleted_count, _ = Purchase.objects.all().delete()
        return Response({'detail': f"{deleted_count} Purchase objects deleted successfully."}, status=status.HTTP_200_OK)

