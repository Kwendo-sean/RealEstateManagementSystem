from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('my-payments/', views.my_payments, name='my_payments'),
    path('initiate/<int:property_id>/', views.initiate_payment, name='initiate_payment'),
    path('pending/<int:transaction_id>/', views.payment_pending, name='payment_pending'),
    path('check-status/<int:transaction_id>/', views.check_payment_status, name='check_payment_status'),
    path('mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
    path('success/', views.payment_success, name='payment_success'),
    path('failed/', views.payment_failed, name='payment_failed'),
]