from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'property', 'client', 'amount', 'status', 'transaction_date']
    list_filter = ['status', 'transaction_date']
    search_fields = ['mpesa_receipt_number', 'phone_number', 'client__username']
    readonly_fields = ['transaction_date', 'created_at', 'updated_at']