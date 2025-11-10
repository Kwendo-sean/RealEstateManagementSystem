from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .mpesa import stk_push
from .models import Payment
import json

@csrf_exempt
def initiate_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
        amount = data.get('amount')

        # Save initial payment
        payment = Payment.objects.create(
            user=request.user,
            phone_number=phone_number,
            amount=amount,
            status='Initiated'
        )

        response = stk_push(phone_number, amount)
        return JsonResponse(response)

@csrf_exempt
def mpesa_callback(request):
    data = json.loads(request.body)
    # Handle M-Pesa callback here (update Payment model)
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})