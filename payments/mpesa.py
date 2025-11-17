import requests
import json
import base64
from datetime import datetime
from django.conf import settings

class MpesaGateway:
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        
    def get_access_token(self):
        """Get MPesa access token"""
        try:
            response = requests.get(
                settings.MPESA_AUTH_URL,
                auth=(self.consumer_key, self.consumer_secret),
                timeout=30
            )
            response.raise_for_status()
            return response.json().get('access_token')
        except Exception as e:
            print(f"Error getting MPesa access token: {e}")
            return None
    
    def generate_password(self):
        """Generate MPesa password as per specification: Shortcode+Passkey+Timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        data_to_encode = self.shortcode + self.passkey + timestamp
        encoded_string = base64.b64encode(data_to_encode.encode()).decode()
        return encoded_string, timestamp
    
    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate STK push request - EXACTLY as per MPesa specification"""
        access_token = self.get_access_token()
        if not access_token:
            return None, "Failed to get access token"
        
        password, timestamp = self.generate_password()
        
        # Format phone number to international format
        phone_number = phone_number.replace('+', '').replace(' ', '')
        if len(phone_number) == 9 and phone_number.startswith('7'):
            phone_number = '254' + phone_number
        elif len(phone_number) == 10 and phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        
        # Prepare payload EXACTLY as per MPesa specification
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": self.shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": account_reference[:12],  
            "TransactionDesc": transaction_desc[:13]     
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            print(f"Sending STK Push request to: {settings.MPESA_STK_PUSH_URL}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                settings.MPESA_STK_PUSH_URL,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {response.text}")
            
            response_data = response.json()
            
            if response.status_code == 200:
                if response_data.get('ResponseCode') == '0':
                    return {
                        'MerchantRequestID': response_data.get('MerchantRequestID'),
                        'CheckoutRequestID': response_data.get('CheckoutRequestID'),
                        'ResponseCode': response_data.get('ResponseCode'),
                        'ResponseDescription': response_data.get('ResponseDescription'),
                        'CustomerMessage': response_data.get('CustomerMessage')
                    }, "STK push initiated successfully"
                else:
                    return response_data, f"STK push failed: {response_data.get('ResponseDescription', 'Unknown error')}"
            else:
                return response_data, f"HTTP Error: {response.status_code} - {response_data.get('errorMessage', 'Unknown error')}"
                
        except requests.exceptions.RequestException as e:
            return None, f"Request failed: {str(e)}"
        except json.JSONDecodeError as e:
            return None, f"Invalid JSON response: {str(e)}"
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"
    
    def query_transaction_status(self, checkout_request_id):
        """Query transaction status"""
        access_token = self.get_access_token()
        if not access_token:
            return None, "Failed to get access token"
        
        password, timestamp = self.generate_password()
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                settings.MPESA_QUERY_URL,
                json=payload,
                headers=headers,
                timeout=30
            )
            return response.json(), "Query completed"
        except Exception as e:
            return None, f"Query request failed: {str(e)}"