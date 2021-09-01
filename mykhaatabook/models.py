from typing import Optional
from django.db import models
from datetime import datetime,date
from django.db.models.fields import AutoField
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.


# Create your models here.
CREDIT = 'Credit'
DEBIT = 'Debit'
NONE = 'None'

TRANSACTION_TYPE_CHOICES = (
    (CREDIT, 'Credit'),
    (DEBIT, 'Debit'),
    (NONE, 'None')
    
)

SIMPLE = '1'
CLEARING = '2'
HAWALA = '3'
BANK = '4'
LAHORE = '5'
CASH = '6'
QARZ = '7'
IRAN = '8'
GADI_KHARCHA = '9'
TAFTAN = '10'




BOOK_TYPE_CHOICES = (
    (SIMPLE, 'Simple'),
    (CLEARING, 'Clearing'),
    (HAWALA, 'Hawala'),
    (BANK, 'Bank'),
    (LAHORE, 'Lahore'),
    (CASH, 'Cash'),
    (QARZ, 'Qarz'),
    (IRAN, 'Iran'),
    (GADI_KHARCHA, 'Gadi_Kharcha'),
    (TAFTAN , 'Taftan')

)



class AccountsBook(models.Model):
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
  
    book_title = models.CharField(max_length=200, help_text="اکونٹ کا نام درج کریں") 
    book_type = models.CharField(
        choices=BOOK_TYPE_CHOICES,
        help_text="اکونٹ کی قسم: sm یا cl",
        max_length=32
    )
    book_created_date = models.DateTimeField()


    def __str__(self):
        return f"{self.book_title}"
    
    def get_absolute_url(self):
        return reverse('accountsbook-detail', args=[str(self.id)])

    class Meta:
        ordering = ['-book_created_date']


class Account(models.Model):
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    date_created = models.DateTimeField()
    title = models.CharField(max_length=200, help_text="اکونٹ کا نام درج کریں")
    phone_number = models.CharField(max_length=11, blank=True, null=True, help_text="۔۔۔اکاؤنٹ کا فون نمبر درج کریں")
    address = models.CharField(max_length=200,null=True,blank=True, help_text="اکاؤنٹ کا پتہ درج کریں")
    amount = models.FloatField(
        null=True,
        default=0,
        blank=True
    ) 
    transaction_type = models.CharField(
        choices=TRANSACTION_TYPE_CHOICES,
        help_text="رقم کی قسم: CR یا DR",
        max_length=32,
        default="Credit",
        blank=True,
        null=True
    )
    book = models.CharField(
        choices=BOOK_TYPE_CHOICES,
        help_text="وہ کھاتہ جہاں سے رقم جمع ہو",
        null=True,
        default='Simple',
        max_length=266
    )
    
    balance = models.FloatField(
        null=True,
        default=0,
        blank=True
    )

    def __str__(self):
        return f"{self.title}"
    
    def get_absolute_url(self):
        return reverse('account-detail', args=[str(self.id)])

    class Meta:
        ordering = ['-date_created']




class Transaction(models.Model):
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    transaction_date = models.DateTimeField()
    refernce_number = models.CharField(default='000000', max_length=366)
    transaction_detail = models.CharField(max_length=210, default="")

    account = models.ForeignKey(
        Account,
        related_name='r_account',
        on_delete=models.CASCADE, help_text="وہ کھاتہ جہاں سے رقم جمع ہو",
        default=0,
         null=True,
         blank=True
    )
    
    bank = models.ForeignKey(
         Account,
         related_name='r_bank',
         on_delete=models.CASCADE,
         help_text="اکاؤنٹ جس میں رقم جمع کی جائے گی",
         default=0,
         null=True,
         blank=True
    )

    transaction_type = models.CharField(
        choices=TRANSACTION_TYPE_CHOICES,
        help_text="رقم کی قسم: کریڈٹ یا ڈیبٹ",
        max_length=32

    ) 
    amount = models.FloatField(
        null=True,
        default=0
    )
    balance_after_transaction = models.FloatField(
        null=True,
        default=0
    )
    slip = models.ImageField(upload_to ='uploads/', null=True)
    


    def __str__(self):
        return f"{self.transaction_type}"

    def get_absolute_url(self):
        return reverse('transaction-detail', args=[str(self.id)])


    class Meta:
        ordering = ['id']
