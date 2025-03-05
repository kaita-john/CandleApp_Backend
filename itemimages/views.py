# Create your views here.
from django.http import JsonResponse
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from utils import SchoolIdMixin, UUID_from_PrimaryKey, DefaultMixin
from .models import ItemImage
from .serializers import ItemImageSerializer


class ItemImageCreateView(SchoolIdMixin, generics.CreateAPIView):
    serializer_class = ItemImageSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({'detail': 'ItemImage created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ItemImageListView(SchoolIdMixin, DefaultMixin, generics.ListAPIView):
    serializer_class = ItemImageSerializer
    def get_queryset(self):
        queryset = ItemImage.objects.all()
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


class ItemImageDetailView(SchoolIdMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = ItemImage.objects.all()
    serializer_class = ItemImageSerializer
    # permission_classes = [IsAuthenticated]

    def get_object(self):
        primarykey = self.kwargs['pk']
        try:
            #id = UUID_from_PrimaryKey(primarykey)
            return ItemImage.objects.get(id=primarykey)
        except (ValueError, ItemImage.DoesNotExist):
            raise NotFound({'detail': 'Record Not Found'})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({'detail': 'ItemImage updated successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': 'Record deleted successfully'}, status=status.HTTP_200_OK)



class ItemImageDeleteAllObjects(SchoolIdMixin, APIView):
    def delete(self, request, *args, **kwargs):
        deleted_count, _ = ItemImage.objects.all().delete()
        return Response({'detail': f"{deleted_count} ItemImage objects deleted successfully."}, status=status.HTTP_200_OK)