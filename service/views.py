# Create your views here.
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from utils import SchoolIdMixin, UUID_from_PrimaryKey, IsAdminOrSuperUser, DefaultMixin
from .models import Service
from .serializers import ServiceSerializer


class ServiceCreateView(SchoolIdMixin, generics.CreateAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({'detail': 'Service created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class ServiceListView(SchoolIdMixin, DefaultMixin, generics.ListAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Service.objects.all()
        academic_year = self.request.query_params.get('academic_year', None)
        if academic_year and academic_year != "" and academic_year != "null":
            queryset = queryset.filter(academic_year=academic_year)
        return queryset


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return JsonResponse({}, status=200)
        serializer = self.get_serializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)



class ServiceDetailView(SchoolIdMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        primarykey = self.kwargs['pk']
        try:
            id = UUID_from_PrimaryKey(primarykey)
            return Service.objects.get(id=id)
        except (ValueError, Service.DoesNotExist):
            raise NotFound({'detail': 'Record Not Found'})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({'detail': 'Service updated successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': 'Record deleted successfully'}, status=status.HTTP_200_OK)



class CurrentServiceView(APIView, DefaultMixin, SchoolIdMixin):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    def get(self, request):
        school_id = self.check_school_id(request)
        if not school_id:
            return JsonResponse({'detail': 'Invalid school_id in token'}, status=401)
        self.check_defaults(self.request, school_id)

        try:
            student = Service.objects.get(is_current=True, school_id = school_id)
            serializer = ServiceSerializer(student, many=False)
        except ObjectDoesNotExist:
            return Response({'detail': f"Current term not set for shool"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': serializer.data}, status=status.HTTP_200_OK)
