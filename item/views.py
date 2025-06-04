# Create your views here.
import json
import threading

from django.http import JsonResponse
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from constants import sender_email, sender_password, COMPANY_EMAIL
from itemimages.models import ItemImage
from utils import SchoolIdMixin, UUID_from_PrimaryKey, DefaultMixin, sendMail
from .models import Item, StockNotification
from .serializers import ItemSerializer
from datetime import datetime



class ItemCreateView(SchoolIdMixin, generics.CreateAPIView):
    serializer_class = ItemSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({'detail': 'Item created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        item = serializer.save()
        other_images = self.request.data.get('itemimages', [])
        for image_url in other_images:
            ItemImage.objects.create(item=item, image=image_url['image'])




class ItemListView(SchoolIdMixin, DefaultMixin, generics.ListAPIView):
    serializer_class = ItemSerializer
    def get_queryset(self):
        queryset = Item.objects.all()
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


class ItemDetailView(SchoolIdMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    # permission_classes = [IsAuthenticated]

    def get_object(self):
        primarykey = self.kwargs['pk']
        try:
            return Item.objects.get(id=primarykey)
        except (ValueError, Item.DoesNotExist):
            raise NotFound({'detail': 'Record Not Found'})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({'detail': 'Item updated successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        item = serializer.save()
        itemimages = self.request.data.get('itemimages', [])
        item.itemimages.all().delete()
        for image_url in itemimages:
            ItemImage.objects.create(item=item, image=image_url['image'])

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': 'Record deleted successfully'}, status=status.HTTP_200_OK)



class ItemDeleteAllObjects(SchoolIdMixin, APIView):
    def delete(self, request, *args, **kwargs):
        deleted_count, _ = Item.objects.all().delete()
        return Response({'detail': f"{deleted_count} Item objects deleted successfully."}, status=status.HTTP_200_OK)


class OutOfStockView(generics.UpdateAPIView):
    queryset = Item.objects.all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.inStock = False
            instance.save()
            return Response({'status': 'success', 'message': 'Item marked as out of stock successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'error', 'message': f'Error marking item as out of stock: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RestockView(generics.UpdateAPIView):
    queryset = Item.objects.all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.inStock = True
            instance.save()
            return Response({'status': 'success', 'message': 'Item restocked successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'error', 'message': f'Error restocking item: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NotifyOutOfStockView(generics.CreateAPIView):
    parser_classes = [JSONParser]

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            name = data.get('name')
            email = data.get('email')
            product_name = data.get('productName')

            if not name or not email or not product_name:
                return Response({'status': 'error', 'message': 'Name, email, and product name are required.'}, status=status.HTTP_400_BAD_REQUEST)
            StockNotification.objects.create(name=name, email=email, product_name=product_name)

            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"""
            Stock Notification Request:

            Name: {name}
            Email: {email}
            Product Name: {product_name}
            Date: {current_date}

            This user has requested to be notified when the product is back in stock.
            """

            threading.Thread(
                target=sendMail,
                args=(sender_email, sender_password, COMPANY_EMAIL, "New Stock Notification Request", message)
            ).start()

            return Response({'status': 'success', 'message': 'Notification request received successfully.'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'status': 'error', 'message': f'Error processing request: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)