# Create your views here.
from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from appuser.models import AppUser
from service.models import Service
from utils import SchoolIdMixin, UUID_from_PrimaryKey, DefaultMixin
from .models import MpesaInvoice
from .serializers import MpesaInvoiceSerializer


class MpesaInvoiceCreateView(SchoolIdMixin, generics.CreateAPIView):
    serializer_class = MpesaInvoiceSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({'detail': 'MpesaInvoice created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class MpesaInvoiceListView(SchoolIdMixin, DefaultMixin, generics.ListAPIView):
    serializer_class = MpesaInvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = MpesaInvoice.objects.all()
        invoice = self.request.query_params.get('invoice', None)
        if invoice and invoice != "" and invoice != "null":
            queryset = queryset.filter(invoice=invoice)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return JsonResponse([], status=200, safe=False)
        serializer = self.get_serializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)


class MpesaInvoiceDetailView(SchoolIdMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = MpesaInvoice.objects.all()
    serializer_class = MpesaInvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        primarykey = self.kwargs['pk']
        try:
            id = UUID_from_PrimaryKey(primarykey)
            return MpesaInvoice.objects.get(id=id)
        except (ValueError, MpesaInvoice.DoesNotExist):
            raise NotFound({'detail': 'Record Not Found'})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({'detail': 'MpesaInvoice updated successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': 'Record deleted successfully'}, status=status.HTTP_200_OK)


class MpesaInvoiceDeleteAllObjects(SchoolIdMixin, APIView):

    def delete(self, request, *args, **kwargs):
        deleted_count, _ = MpesaInvoice.objects.all().delete()
        return Response({'detail': f"{deleted_count} MpesaInvoice objects deleted successfully."},
                        status=status.HTTP_200_OK)
