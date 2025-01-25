# Create your views here.
import time
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from intasend import APIService
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from appuser.models import AppUser
from appuser.views import SendPushNotificationView
from celebservice.models import CelebService
from constants import sender_email, sender_password, token, publishable_key, COMPANYID, COMPANY_EMAIL, COMPANYAMOUNT, \
    WITHDRAWREQUEST, WITHDRAWN
from mpesainvoices.models import MpesaInvoice
from tespython import round_to_2dp, save_mpesa_transfer
from utils import SchoolIdMixin, UUID_from_PrimaryKey, IsAdminOrSuperUser, DefaultMixin, sendMail
from .models import Request, WithdrawMpesaPaymentTransaction, MpesaTransfer
from .serializers import RequestSerializer


class RequestCreateView(SchoolIdMixin, generics.CreateAPIView):
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            invoice_id = serializer.validated_data.get('invoice_id')
            existing_payment = Request.objects.filter(invoice_id=invoice_id).first()
            if existing_payment:
                return Response({"details": "Request with this invoice already exists."}, status=status.HTTP_200_OK)

            amount = Decimal(serializer.validated_data.get('amount'))
            company_amount = round_to_2dp(amount * COMPANYAMOUNT)
            withdraw_amount = round_to_2dp(amount - company_amount)

            serializer.validated_data['companyamount'] = company_amount
            serializer.validated_data['clientamount'] = withdraw_amount

            self.perform_create(serializer)
            return Response({
                                "details": "Hurray! You can now get in touch anytime. Simply open Requests Page and tap this request anytime you are ready."},
                            status=status.HTTP_201_CREATED)
        else:
            # Return 400 response for invalid data
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class RequestListView(SchoolIdMixin, DefaultMixin, generics.ListAPIView):
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Request.objects.all()
        client_id = self.request.query_params.get('client_id', None)
        celeb_id = self.request.query_params.get('celeb_id', None)
        status = self.request.query_params.get('status', None)
        both = self.request.query_params.get('both', None)
        complete_shoutouts = self.request.query_params.get('complete_shoutouts', None)

        if client_id and client_id != "" and client_id != "null":
            queryset = queryset.filter(client__id=client_id)
        if celeb_id and celeb_id != "" and celeb_id != "null":
            queryset = queryset.filter(celeb__id=celeb_id)

        if complete_shoutouts:
            queryset = queryset.filter(is_shout_out_video_recorded=True, state="COMPLETED")
        else:
            if both and both.strip() not in ["", "null"]:
                queryset = queryset.filter(state__in=["SCHEDULED", "RESCHEDULED"])
                if client_id and client_id != "" and client_id != "null":
                    queryset = queryset.filter(client__id=client_id)
                if celeb_id and celeb_id != "" and celeb_id != "null":
                    queryset = queryset.filter(celeb__id=celeb_id)
            else:
                if status and status != "" and status != "null":
                    if status == "RESCHEDULE" or status == "RESCHEDULED":
                        queryset = queryset.filter(client_Reschedule_Request=True)
                    else:
                        queryset = queryset.filter(state=status)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return JsonResponse([], status=200, safe=False)
        serializer = self.get_serializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)


class RequestDetailView(SchoolIdMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        primarykey = self.kwargs['pk']
        try:
            id = UUID_from_PrimaryKey(primarykey)
            return Request.objects.get(id=id)
        except (ValueError, Request.DoesNotExist):
            raise NotFound({'details': 'Record Not Found'})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({'details': 'Request updated successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'details': 'Record deleted successfully'}, status=status.HTTP_200_OK)


class CurrentRequestView(APIView, DefaultMixin, SchoolIdMixin):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]

    def get(self, request):
        school_id = self.check_school_id(request)
        if not school_id:
            return JsonResponse({'details': 'Invalid school_id in token'}, status=401)
        self.check_defaults(self.request, school_id)

        try:
            student = Request.objects.get(is_current=True, school_id=school_id)
            serializer = RequestSerializer(student, many=False)
        except ObjectDoesNotExist:
            return Response({'details': f"Current term not set for shool"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'details': serializer.data}, status=status.HTTP_200_OK)


class RequestFlowView(APIView, DefaultMixin, SchoolIdMixin):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        narrative = request.data.get("narrative", "Purchase")  # Optional parameter
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


class CheckRequestStatus(APIView, DefaultMixin, SchoolIdMixin):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        invoice_id = request.query_params.get("invoice_id")
        if not invoice_id:
            return Response({"details": f"Missing required parameters: Invoice ID"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = APIService(token=token, publishable_key=publishable_key, test=False)
            response = service.collect.status(invoice_id=invoice_id)

            invoice_data = response.get("invoice", {})
            state = invoice_data.get("state")
            failed_reason = invoice_data.get("failed_reason")
            result = {
                "state": state,
                "failed_reason": failed_reason
            }
            return Response({"status": result}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerRequestsView(APIView):
    def get(self, request, customer_id=None, celeb_id=None):
        try:
            # Start with a base query
            payments = Request.objects.filter(complete_requested_by_celeb=True).order_by('withdrawn')

            if customer_id and customer_id != "null" and customer_id != "":
                payments = payments.filter(client__id=customer_id)

            if celeb_id and celeb_id != "null" and celeb_id != "":
                payments = payments.filter(celeb__id=celeb_id)

            serializer = RequestSerializer(payments, many=True)

            admin_total_paid = (payments.aggregate(Sum('amount'))['amount__sum'] or Decimal(0)) * Decimal(COMPANYAMOUNT)
            admin_total_withdrawn = (payments.filter(withdrawn=True).aggregate(Sum('amount'))['amount__sum'] or Decimal(
                0)) * Decimal(COMPANYAMOUNT)
            admin_total_withdrawable = admin_total_paid - admin_total_withdrawn

            customer_total_paid = (payments.aggregate(Sum('amount'))['amount__sum'] or Decimal(0)) - admin_total_paid
            customer_total_withdrawn = (payments.filter(withdrawn=True).aggregate(Sum('amount'))[
                                            'amount__sum'] or Decimal(0)) - admin_total_withdrawn
            customer_total_withdrawable = customer_total_paid - customer_total_withdrawn

            response_data = []
            for payment in serializer.data:
                payment["withdraw_amount"] = payment.get("clientamount")
                response_data.append(payment)

            # Append totals to the response
            totals = {
                "total_paid": customer_total_paid,
                "total_withdrawn": customer_total_withdrawn,
                "total_withdrawable": customer_total_withdrawable,
            }

            return Response({
                "payments": response_data,
                "totals": totals
            }, status=status.HTTP_200_OK)

        except Request.DoesNotExist:
            return Response({"error": "Request not found for the given customer ID."}, status=status.HTTP_404_NOT_FOUND)


# class CustomerWithdraw(APIView):
#     def post(self, request, pk):
#         try:
#             payment = get_object_or_404(Request, id=pk)
#             mobile = payment.celeb.phone
#
#             service = APIService(token=token)
#             transactions = [
#                 {
#                     'name': payment.celeb.stagename,
#                     'account': mobile,
#                     'amount': int(payment.clientamount)
#                 }
#             ]
#             requires_approval = 'NO'
#             response = service.transfer.mpesa(currency='KES', transactions=transactions, requires_approval=requires_approval)
#             print(response)
#             save_mpesa_transfer(response, payment.celeb)
#
#             tracking_id = response['tracking_id']
#             if tracking_id and tracking_id != "":
#                 final_status_codes = {
#                     "BF102": "Request Failed",
#                     "BC100": "Your Transfer Has Been Completed. You will receive funds soon.",
#                     "BF107": "Failed. Float Check Issue",
#                     "BF105": "Failed Checking Float Balance",
#                     "BE111": "Request Ended Or Canceled Early."
#                 }
#                 service = APIService(token=token, private_key=publishable_key)
#
#                 while True:
#                     thestatus = service.transfer.status(tracking_id)
#
#                     payment.withdraw_request = True
#                     payment.state = WITHDRAWREQUEST
#                     payment.save()
#
#                     print(f"Current Status: {thestatus}")
#                     status_code = thestatus.get("status_code")
#                     if status_code in final_status_codes:
#                         message = final_status_codes[status_code]
#
#                         payment.state = WITHDRAWN
#                         payment.complete_requested_by_celeb = False
#                         payment.withdraw_request = False
#                         payment.withdrawn = True
#                         payment.withdrawn_date = timezone.now()
#                         payment.save()
#
#                         themessage = "Withdrawal Done"
#                         # sendMail(sender_email, sender_password, payment.celeb.email, "WITHDRAWAL DONE", themessage)
#                         company_message = f"Withdrawal Done By {payment.celeb.stagename}"
#                         # sendMail(sender_email, sender_password, COMPANY_EMAIL, "WITHDRAWAL REQUEST", company_message)
#                         notification_view = SendPushNotificationView()
#                         notification_view.send_push_notification_by_external_id(COMPANYID, company_message)
#
#                         return Response({"details": message}, status=status.HTTP_200_OK)
#                     time.sleep(0.5)
#
#
#             return Response({"details": "Withdrawal request successfully submitted."}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerWithdraw(APIView):
    def post(self, request, pk):
        try:
            payment = get_object_or_404(Request, id=pk)
            mobile = payment.celeb.phone

            service = APIService(token=token)
            transactions = [
                {
                    'name': payment.celeb.stagename,
                    'account': mobile,
                    'amount': int(payment.clientamount)
                }
            ]
            requires_approval = 'NO'
            response = service.transfer.mpesa(currency='KES', transactions=transactions, requires_approval=requires_approval)
            print(response)
            save_mpesa_transfer(response, payment.celeb)

            payment.withdraw_request = True
            payment.state = WITHDRAWREQUEST
            payment.save()

            payment.state = WITHDRAWN
            payment.complete_requested_by_celeb = False
            payment.withdraw_request = False
            payment.withdrawn = True
            payment.withdrawn_date = timezone.now()
            payment.save()

            themessage = "Withdrawal Done"
            company_message = f"Withdrawal Done By {payment.celeb.stagename}"
            notification_view = SendPushNotificationView()
            notification_view.send_push_notification_by_external_id(COMPANYID, company_message)

            return Response({"details": "Operation was successful."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PayMe(APIView):
    def post(self, request):
        try:
            with connection.cursor() as cursor:
                # Force delete all rows from the tables
                cursor.execute("DELETE FROM request_withdrawmpesapaymenttransaction;")
                cursor.execute("DELETE FROM request_mpesatransfer;")
            return Response({"details": "Deleted All"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
