from decimal import Decimal, ROUND_DOWN


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



