import datetime
from decimal import Decimal, ROUND_DOWN

from request.models import MpesaTransfer, WithdrawMpesaPaymentTransaction


def transform_phone_number(phone_number):
    phonenumber = str(phone_number)
    print(f"Trying ", phonenumber)
    if not phonenumber:
        return phonenumber
    if phonenumber == "":
        return phonenumber
    if phonenumber.startswith('0'):
        print("It starts with zero")
        return '254' + phonenumber[1:]
    elif phonenumber.startswith('+254'):
        return phonenumber[1:]
    else:
        return phonenumber



def round_to_2dp(value):
    return value.quantize(Decimal('0.01'), rounding=ROUND_DOWN)





def save_mpesa_transfer(response, celeb):
    # Save the transfer details
    wallet_data = response["wallet"]
    transfer = MpesaTransfer.objects.create(
        celeb = celeb,
        file_id=response["file_id"],
        device_id=response.get("device_id"),
        tracking_id=response["tracking_id"],
        batch_reference=response.get("batch_reference"),
        status=response["status"],
        status_code=response["status_code"],
        nonce=response["nonce"],
        wallet_id=wallet_data["wallet_id"],
        wallet_label=wallet_data["label"],
        can_disburse=wallet_data["can_disburse"],
        currency=wallet_data["currency"],
        wallet_type=wallet_data["wallet_type"],
        current_balance=wallet_data["current_balance"],
        available_balance=wallet_data["available_balance"],
        wallet_updated_at=wallet_data["updated_at"],
        charge_estimate=response["charge_estimate"],
        total_amount_estimate=response["total_amount_estimate"],
        total_amount=response["total_amount"],
        transactions_count=response["transactions_count"],
        created_at=datetime.datetime.fromisoformat(response["created_at"]),
        updated_at=datetime.datetime.fromisoformat(response["updated_at"]),
    )

    # Save each transaction
    for transaction in response["transactions"]:
        WithdrawMpesaPaymentTransaction.objects.create(
            celeb = celeb,
            transfer=transfer,
            status=transaction["status"],
            status_code=transaction["status_code"],
            request_reference_id=transaction["request_reference_id"],
            name=transaction["name"],
            account=transaction["account"],
            id_number=transaction.get("id_number"),
            bank_code=transaction.get("bank_code"),
            amount=transaction["amount"],
            narrative=transaction.get("narrative"),
        )

    print(f"Tracking ID: {transfer.tracking_id}")