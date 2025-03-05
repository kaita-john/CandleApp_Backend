import time

from django.db import transaction
from intasend import APIService
from rest_framework import serializers

from constants import token, publishable_key
from mpesainvoices.models import MpesaInvoice
from purchase.models import Purchase
from purchaseitem.models import PurchaseItem
from purchaseitem.serializers import PurchaseItemSerializer



class PurchaseSerializer(serializers.ModelSerializer):
    purchaseitems = PurchaseItemSerializer(many=True)

    class Meta:
        model = Purchase
        fields = '__all__'
        read_only_fields = ['total_price']

    def create(self, validated_data):
        purchaseitems_data = validated_data.pop('purchaseitems')
        mobile = validated_data.get("mobile")
        email = validated_data.get("email")

        if not mobile or not email:  # Check for both mobile and email
            raise serializers.ValidationError({"error": "Mobile and email are required for payment"})

        total_price = 0
        for item in purchaseitems_data:
            purchaseItem = PurchaseItem(**item)  # Don't create yet
            total_price += purchaseItem.price * purchaseItem.quantity

        amount = total_price

        service = APIService(token=token, publishable_key=publishable_key, test=False)
        response = service.collect.mpesa_stk_push(
            phone_number=int(mobile),
            email=email,
            amount=int(amount),
            narrative="purchase",  # Narrative can be a string literal
        )

        invoice = response.get("invoice", {})
        invoice_id = invoice.get("invoice_id")

        if not invoice or not invoice_id:
            raise serializers.ValidationError({"error": "Failed to initiate payment"})

        if MpesaInvoice.objects.filter(invoice=invoice_id).exists():
            raise serializers.ValidationError({"error": "Duplicate invoice detected"})

        MpesaInvoice.objects.create(invoice=invoice_id)

        service = APIService(token=token, publishable_key=publishable_key, test=False)
        purchase = None # Initialize purchase outside the loop

        for _ in range(100000000):
            response = service.collect.status(invoice_id=invoice_id)
            invoice_data = response.get("invoice", {})
            state = invoice_data.get("state")
            failed_reason = invoice_data.get("failed_reason")

            print(f"Current Status: {state}")

            if state == "COMPLETED" or state == "COMPLETE":
                with transaction.atomic(): # Create Purchase only after successful payment
                    purchase = Purchase.objects.create(**validated_data) # Create Purchase here
                    purchase.total_price = total_price
                    purchase.save()
                    for item in purchaseitems_data:
                        purchaseItem = PurchaseItem.objects.create(**item)
                        purchase.purchaseitems.add(purchaseItem)
                return purchase # Return the Purchase object
            elif state in ["FAILED", "CANCELLED"]:
                raise serializers.ValidationError({"error": f"Payment {state}. Reason: {failed_reason or 'Unknown'}"}) # Raise exception on failure
            elif state == "PROCESSING":
                pass # Continue checking
            elif state == "PENDING":
                pass # Continue checking

            time.sleep(1)

        raise serializers.ValidationError({"error": "Payment timed out."})



    def update(self, instance, validated_data):
        purchaseitems_list = validated_data.pop('purchaseitems', [])
        # Update other fields of the purchase instancess
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.purchaseitems.clear()

        for purchaseitem in purchaseitems_list:
            purchaseItem = PurchaseItem.objects.create(**purchaseitem)
            instance.purchaseitems.add(purchaseItem)

        return instance