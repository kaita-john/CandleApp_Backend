import json
import threading
import time

from django.db import transaction
from intasend import APIService
from intasend.exceptions import IntaSendBadRequest
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from constants import token, publishable_key, sender_email, sender_password, COMPANY_EMAIL
from mpesainvoices.models import MpesaInvoice
from utils import sendMail
from .models import CandleClassBooking


class CandleClassBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandleClassBooking
        fields = '__all__'

    def create(self, validated_data):
        mobile = validated_data.get("phoneNumber")
        email = validated_data.get("email")
        amount = validated_data.get("amount")

        if not mobile or not email or not amount:  # Check for both mobile and email
            raise serializers.ValidationError({"error": "Mobile, email and amount are required for payment"})

        service = APIService(token=token, publishable_key=publishable_key, test=False)

        try:
            response = service.collect.mpesa_stk_push(
                phone_number=int(mobile),
                email=email,
                amount=int(amount),
                narrative="candleclassbooking",
            )
        except IntaSendBadRequest as e:
            try:
                # Convert string to dict
                err_detail = json.loads(e.args[0])  # Use e.args[0] instead of str(e)
                print(err_detail)

                # Collect all error messages (in case there are multiple)
                error_messages = [err["detail"] for err in err_detail.get("errors", [])]
                raise ValidationError({"mpesa": error_messages})
            except Exception as parse_error:
                print("Error parsing IntaSend error:", parse_error)
                raise ValidationError({"mpesa": "STK Push failed. Please check phone number format."})

        invoice = response.get("invoice", {})
        invoice_id = invoice.get("invoice_id")

        if not invoice or not invoice_id:
            raise serializers.ValidationError({"error": "Failed to initiate payment"})

        if MpesaInvoice.objects.filter(invoice=invoice_id).exists():
            raise serializers.ValidationError({"error": "Duplicate invoice detected"})

        MpesaInvoice.objects.create(invoice=invoice_id)

        service = APIService(token=token, publishable_key=publishable_key, test=False)
        purchase = None # Initialize purchase outside the loop

        message = (
            f"🕯️ New Candle Class Booking 🕯️\n\n"
            f"Name: {validated_data.get('fullName')}\n"
            f"Email: {email}\n"
            f"Mobile: {mobile}\n"
            f"Amount: {amount}\n"
            f"Class Date: {validated_data.get('availableDateTime')}\n"
            f"\nPlease check admin panel for more details."
        )

        for _ in range(100000000):
            response = service.collect.status(invoice_id=invoice_id)
            invoice_data = response.get("invoice", {})
            state = invoice_data.get("state")
            failed_reason = invoice_data.get("failed_reason")
            print(f"Current Status: {state}")
            if state == "COMPLETED" or state == "COMPLETE":
                with transaction.atomic():
                    candleclassbooking = CandleClassBooking.objects.create(**validated_data)
                    candleclassbooking.save()
                    # Start background email thread
                    threading.Thread(
                        target=sendMail,
                        args=(sender_email, sender_password, COMPANY_EMAIL, "New Candle Class Booking", message)
                    ).start()
                return candleclassbooking
            elif state in ["FAILED", "CANCELLED"]:
                raise serializers.ValidationError({"error": f"Payment {state}. Reason: {failed_reason or 'Unknown'}"}) # Raise exception on failure
            elif state == "PROCESSING":
                pass # Continue checking
            elif state == "PENDING":
                pass # Continue checking
            time.sleep(1)

        raise serializers.ValidationError({"error": "Payment timed out."})
