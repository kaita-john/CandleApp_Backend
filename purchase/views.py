# Create your views here.
from django.http import JsonResponse
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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





class RequestFlowView(APIView, DefaultMixin, SchoolIdMixin):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        narrative = request.data.get("narrative", "Purchase")
        mobile = request.data.get("mobile")
        email = request.data.get("email")
        amount = request.data.get("amount")
        client = request.data.get("client")
        celebservice = request.data.get("celebservice")

        missing_params = []
        if not mobile:
            missing_params.append("mobile")
        if not email:
            missing_params.append("email")
        if not amount:
            missing_params.append("amount")
        if not client:
            missing_params.append("client")
        if not celebservice:
            missing_params.append("celebservice")

        # Validate required parameters
        if missing_params:
            return Response({"details": f"Missing required parameters: {', '.join(missing_params)}"},
                            status=status.HTTP_400_BAD_REQUEST)

        client = AppUser.objects.get(id=client)
        if client is None:
            return Response({'detail': f"Invalid Client ID"}, status=status.HTTP_400_BAD_REQUEST)
        celebservice = CelebService.objects.get(id=celebservice)
        if celebservice is None:
            return Response({'detail': f"Invalid Celeb Service ID"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = APIService(token=token, publishable_key=publishable_key, test=False)
            # Trigger the Mpesa STK Push
            response = service.collect.mpesa_stk_push(
                phone_number=int(mobile),
                email=email,
                amount=int(amount),
                narrative=narrative,
            )

            invoice = response.get("invoice", {})
            if not invoice: return Response({"detail": "Invoice not found in the response."},
                                            status=status.HTTP_404_NOT_FOUND, )

            existing_invoice = MpesaInvoice.objects.filter(invoice=invoice.get("invoice_id")).first()
            if existing_invoice:
                return Response({"detail": "Invoice already exists."}, status=status.HTTP_400_BAD_REQUEST)

            MpesaInvoice.objects.create(celebservice=celebservice, client=client,
                                        invoice=invoice.get("invoice_id", "None"))

            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:

            return Response({"details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)