# Create your views here.
from django.http import JsonResponse
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from utils import SchoolIdMixin, DefaultMixin
from .models import CandleClassBooking
from .serializers import CandleClassBookingSerializer


class CandleClassBookingCreateView(SchoolIdMixin, generics.CreateAPIView):
    serializer_class = CandleClassBookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({'detail': 'CandleClassBooking created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CandleClassBookingListView(SchoolIdMixin, DefaultMixin, generics.ListAPIView):
    serializer_class = CandleClassBookingSerializer
    def get_queryset(self):
        queryset = CandleClassBooking.objects.all()
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


class CandleClassBookingDetailView(SchoolIdMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = CandleClassBooking.objects.all()
    serializer_class = CandleClassBookingSerializer
    # permission_classes = [IsAuthenticated]

    def get_object(self):
        primarykey = self.kwargs['pk']
        try:
            #id = UUID_from_PrimaryKey(primarykey)
            return CandleClassBooking.objects.get(id=primarykey)
        except (ValueError, CandleClassBooking.DoesNotExist):
            raise NotFound({'detail': 'Record Not Found'})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({'detail': 'CandleClassBooking updated successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': 'Record deleted successfully'}, status=status.HTTP_200_OK)



class CandleClassBookingDeleteAllObjects(SchoolIdMixin, APIView):
    def delete(self, request, *args, **kwargs):
        deleted_count, _ = CandleClassBooking.objects.all().delete()
        return Response({'detail': f"{deleted_count} CandleClassBooking objects deleted successfully."}, status=status.HTTP_200_OK)