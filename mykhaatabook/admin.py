from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *
# Register your models here.

class AccountAdmin(admin.ModelAdmin):
    list_display = ('operator', 'id', 'book','date_created', 'title', 'phone_number', 'address', 'balance')
    list_filter = ('operator','date_created', 'balance' , 'title', 'book')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('operator',  'id', 'refernce_number','transaction_date','transaction_detail', 'account', 'bank', 'transaction_type', 'amount', 'balance_after_transaction', 'slip')
    list_filter = ('operator','transaction_date', 'account', 'bank', 'transaction_type', 'amount', 'slip')
    

admin.site.register(Account, AccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(AccountsBook)