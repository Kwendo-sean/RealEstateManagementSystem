import requests
import base64
from datetime import datetime
from django.conf import settings

def get_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_URL = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"

    response = requests.get(api_URL, auth=(consumer_key, consumer_secret))
    access_token = response.json().get('access_token')
    return access_token


def stk_push(phone_number, amount, account_reference="RealEstate", transaction_desc="Property Payment"):
    access_token = get_access_token()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode()).decode('utf-8')

    api_url = f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://your-domain.com/payments/callback/",
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc,
    }

    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()