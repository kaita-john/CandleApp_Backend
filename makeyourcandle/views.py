# Create your views here.
import threading

from django.http import JsonResponse
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from constants import sender_email, sender_password, COMPANY_EMAIL
from utils import SchoolIdMixin, DefaultMixin, sendMail
from .models import MakeYourCandle
from .serializers import MakeYourCandleSerializer


class MakeYourCandleCreateView(SchoolIdMixin, generics.CreateAPIView):
    serializer_class = MakeYourCandleSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            self.perform_create(serializer)
            message = f"""
            New MakeYourCandle Order:
            Purpose: {data.get('purpose')}
            Quantity: {data.get('quantity')}
            Scent: {data.get('scent')}
            Jar Color: {data.get('jar_color')}
            Special Labeling: {data.get('special_labeling')}
            Custom Message: {data.get('custom_message')}
            Delivery Timeline: {data.get('delivery_timeline')}
            Additional Notes: {data.get('additional_notes')}
            Email: {data.get('email')}
            Phone Number: {data.get('phone_number')}
            """
            # Send email asynchronously
            threading.Thread(
                target=sendMail,
                args=(sender_email, sender_password, COMPANY_EMAIL, "New MakeYourCandle Order", message)
            ).start()
            return Response({'detail': 'MakeYourCandle created successfully'}, status=status.HTTP_201_CREATED)

        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class MakeYourCandleListView(SchoolIdMixin, DefaultMixin, generics.ListAPIView):
    serializer_class = MakeYourCandleSerializer
    def get_queryset(self):
        queryset = MakeYourCandle.objects.all()
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


class MakeYourCandleDetailView(SchoolIdMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = MakeYourCandle.objects.all()
    serializer_class = MakeYourCandleSerializer
    # permission_classes = [IsAuthenticated]

    def get_object(self):
        primarykey = self.kwargs['pk']
        try:
            #id = UUID_from_PrimaryKey(primarykey)
            return MakeYourCandle.objects.get(id=primarykey)
        except (ValueError, MakeYourCandle.DoesNotExist):
            raise NotFound({'detail': 'Record Not Found'})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({'detail': 'MakeYourCandle updated successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': 'Record deleted successfully'}, status=status.HTTP_200_OK)



class MakeYourCandleDeleteAllObjects(SchoolIdMixin, APIView):
    def delete(self, request, *args, **kwargs):
        deleted_count, _ = MakeYourCandle.objects.all().delete()
        return Response({'detail': f"{deleted_count} MakeYourCandle objects deleted successfully."}, status=status.HTTP_200_OK)