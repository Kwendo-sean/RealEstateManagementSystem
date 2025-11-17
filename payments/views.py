from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from decimal import Decimal
from properties.models import Property
from .models import Transaction
from .mpesa import MpesaGateway

@login_required
def my_payments(request):
    """View for clients to see their payment history"""
    if request.user.role != 'client':
        messages.error(request, 'Only clients can view payment history.')
        return redirect('properties:property_list')
    
    transactions = Transaction.objects.filter(client=request.user).select_related('property').order_by('-created_at')
    
    context = {
        'transactions': transactions,
    }
    return render(request, 'payments/my_payments.html', context)

@login_required
def initiate_payment(request, property_id):
    """Initiate MPesa payment for a property"""
    if request.user.role != 'client':
        messages.error(request, 'Only clients can make payments.')
        return redirect('properties:property_list')
    
    property = get_object_or_404(Property, id=property_id)
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        amount = property.price
        
        if not phone_number:
            messages.error(request, 'Please provide a phone number.')
            return render(request, 'payments/initiate_payment.html', {'property': property})
        
        # Create transaction record
        transaction = Transaction.objects.create(
            property=property,
            client=request.user,
            amount=amount,
            phone_number=phone_number,
            status='pending'
        )
        
        # Initialize MPesa gateway
        mpesa = MpesaGateway()
        
        # Prepare account reference and description
        account_reference = f"PROP{property.id}"[:12]  
        transaction_desc = f"Property {property.id}"[:13]  
        
        # Initiate STK push
        response_data, message = mpesa.stk_push(
            phone_number=phone_number,
            amount=amount,
            account_reference=account_reference,
            transaction_desc=transaction_desc
        )
        
        if response_data and response_data.get('ResponseCode') == '0':
            # Save MPesa response details exactly as received
            transaction.merchant_request_id = response_data.get('MerchantRequestID', '')
            transaction.checkout_request_id = response_data.get('CheckoutRequestID', '')
            transaction.result_code = 0  # Set to 0 for successful initiation
            transaction.result_desc = response_data.get('ResponseDescription', '')
            transaction.save()
            
            messages.success(request, f"{response_data.get('CustomerMessage', 'Payment request sent to your phone. Please check your MPesa menu to complete the payment.')}")
            return redirect('payments:payment_pending', transaction_id=transaction.id)
        else:
            transaction.status = 'failed'
            transaction.result_desc = message
            transaction.save()
            
            error_message = response_data.get('ResponseDescription', message) if response_data else message
            messages.error(request, f'Failed to initiate payment: {error_message}')
            return render(request, 'payments/initiate_payment.html', {'property': property})
    
    context = {
        'property': property,
    }
    return render(request, 'payments/initiate_payment.html', context)

@login_required
def payment_pending(request, transaction_id):
    """Show payment pending page while waiting for MPesa callback"""
    transaction = get_object_or_404(Transaction, id=transaction_id, client=request.user)
    
    context = {
        'transaction': transaction,
        'property': transaction.property,
    }
    return render(request, 'payments/payment_pending.html', context)

@login_required
def check_payment_status(request, transaction_id):
    """AJAX endpoint to check payment status"""
    transaction = get_object_or_404(Transaction, id=transaction_id, client=request.user)
    
    return JsonResponse({
        'status': transaction.status,
        'result_desc': transaction.result_desc,
        'mpesa_receipt': transaction.mpesa_receipt_number
    })

@csrf_exempt
@require_POST
def mpesa_callback(request):
    """MPesa callback endpoint - handles the EXACT callback format from MPesa"""
    try:
        callback_data = json.loads(request.body)
        print(f"Received MPesa callback: {json.dumps(callback_data, indent=2)}")
        
        # Extract data from the exact callback format
        stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
        merchant_request_id = stk_callback.get('MerchantRequestID')
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')
        
        print(f"Processing callback: MerchantRequestID={merchant_request_id}, CheckoutRequestID={checkout_request_id}, ResultCode={result_code}")
        
        # Find transaction
        try:
            transaction = Transaction.objects.get(checkout_request_id=checkout_request_id)
            
            if result_code == 0:
                # Payment successful - extract callback metadata
                transaction.status = 'completed'
                transaction.result_code = result_code
                transaction.result_desc = result_desc
                
                # Extract metadata from callback
                callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                metadata_dict = {}
                
                for item in callback_metadata:
                    metadata_dict[item.get('Name')] = item.get('Value')
                
                # Update transaction with MPesa details
                transaction.mpesa_receipt_number = metadata_dict.get('MpesaReceiptNumber', '')
                if 'PhoneNumber' in metadata_dict:
                    transaction.phone_number = str(metadata_dict['PhoneNumber'])
                if 'Amount' in metadata_dict:
                    transaction.amount = Decimal(str(metadata_dict['Amount']))
                
                transaction.save()
                
                print(f"Payment completed successfully for transaction {transaction.id}")
                print(f"MPesa Receipt: {transaction.mpesa_receipt_number}")
                
            else:
                # Payment failed or cancelled
                transaction.status = 'failed'
                transaction.result_code = result_code
                transaction.result_desc = result_desc
                transaction.save()
                
                print(f"Payment failed for transaction {transaction.id}: {result_desc}")
                
        except Transaction.DoesNotExist:
            print(f"Transaction not found for checkout request: {checkout_request_id}")
            # Still return success to MPesa to avoid retries
        
        # ALWAYS return success to MPesa as per specification
        response_data = {
            "ResultCode": 0,
            "ResultDesc": "Success"
        }
        return JsonResponse(response_data)
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error in MPesa callback: {e}")
        print(f"Raw callback data: {request.body}")
        response_data = {
            "ResultCode": 0,
            "ResultDesc": "Success"
        }
        return JsonResponse(response_data)
    except Exception as e:
        print(f"Unexpected error processing MPesa callback: {e}")
        response_data = {
            "ResultCode": 0,
            "ResultDesc": "Success"
        }
        return JsonResponse(response_data)

def payment_success(request):
    """Payment success page"""
    return render(request, 'payments/payment_success.html')

def payment_failed(request):
    """Payment failed page"""
    return render(request, 'payments/payment_failed.html')