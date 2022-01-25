import tempfile
import random
from datetime import datetime as dt
from xmlrpc.client import _datetime_type
from django.db.models import Sum
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import request, response
from django.http.response import Http404
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from . models import *
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
import sys
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import NewUserForm
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth import login, authenticate, logout
from django.template.loader import get_template, render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm

from weasyprint import HTML
from datetime import datetime, date
import pytz
from django.utils.datastructures import MultiValueDictKeyError
# Create your views here.


def register_request(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect('index')
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request=request, template_name="home/register.html", context={"register_form":form})

def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("index")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="home/login.html", context={"login_form":form})

def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("login")


def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "password/password_reset_email.txt"
					c = {
					"email":user.email,
					'domain':'127.0.0.1:8000',
					'site_name': 'Website',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'admin@example.com' , [user.email], fail_silently=False)
					except BadHeaderError:

						return HttpResponse('Invalid header found.')
						
					messages.success(request, 'A message with reset password instructions has been sent to your email inbox.')
					return redirect ("password_reset_done")
			messages.error(request, 'An invalid email has been entered.')
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="password/password_reset.html", context={"password_reset_form":password_reset_form})


def get_bookAllaccTotal(request,book_num):
    all_accounts_in_book = Account.objects.filter(operator__exact = request.user).filter(book__exact = str(book_num))
    account_balance_list = []
    account_balance_total = 0
    for acc in all_accounts_in_book:
        account = Account.objects.filter(operator__exact = request.user).get(pk = acc.id)
        trans1 = account.from_account.filter(operator__exact = request.user).all()
        trans2 = account.to_account.filter(operator__exact = request.user).all()
        transaction_list =  trans1 | trans2
        for transaction in transaction_list:
                # print('Transaction:', transaction.account, transaction.bank, transaction )
                #Executed when new account is created 
                if transaction.transaction_type == DEBIT and  transaction.account == account and  transaction.bank == None:
                    account_balance_total = account_balance_total + transaction.amount
                    account_balance_list.append(account_balance_total)                 
                    # print('Debit 1: ', account_balance)            
                #Executed when new account is created 
                if transaction.transaction_type == CREDIT and  transaction.account == account and  transaction.bank == None:
                    account_balance_total = account_balance_total - transaction.amount
                    account_balance_list.append(account_balance_total)
                    # print('Credited 2: ', account_balance)
                #Executed when the current account is Credit account and transaction list is debited 
                if transaction.transaction_type == DEBIT and  transaction.account == account and  transaction.bank != None:
                    account_balance_total = account_balance_total - transaction.amount
                    account_balance_list.append(account_balance_total)
                    # print('Debit 2: ', account_balance)
                
                #Executed when the current account is Credit account and transaction list is credited
                if transaction.transaction_type == CREDIT and  transaction.account == account and  transaction.bank != None:
                    account_balance_total = account_balance_total - transaction.amount
                    account_balance_list.append(account_balance_total)
                    # print('Credited 1: ', account_balance)
                
                 #Executed when the current account is Credit account and transaction list is None
                if transaction.transaction_type == NONE and  transaction.account == account and  transaction.bank != None:
                    account_balance_total = account_balance_total - transaction.amount
                    account_balance_list.append(account_balance_total)
                    # print('None 1: ', account_balance)
         
                                
                #Executed when the current account is Debit account and transaction list is debited
                if transaction.transaction_type == DEBIT and  transaction.bank == account and  transaction.bank != None:
                    account_balance_total = account_balance_total + transaction.amount
                    account_balance_list.append(account_balance_total)
                    # print('Debited 3: ', account_balance)
                
                #Executed when the current account is Debit account and transaction list is credited
                if transaction.transaction_type == CREDIT and  transaction.bank == account and  transaction.bank != None:
                    account_balance_total = account_balance_total + transaction.amount
                    account_balance_list.append(account_balance_total)
                    # print('Credited 3: ', account_balance)
                
                #Executed when the current account is Debit account and transaction list is None
                if transaction.transaction_type == NONE and  transaction.bank == account and  transaction.bank != None:
                    account_balance_total = account_balance_total + transaction.amount
                    account_balance_list.append(account_balance_total)

    return account_balance_list

    
@login_required
def index(request):
    num_books = AccountsBook.objects.filter(operator__exact = request.user).count()

    num_accounts = Account.objects.filter(operator__exact = request.user).count()

    num_bank_accounts= Account.objects.filter(operator__exact = request.user).filter(book__exact = '4').count()
    # all banks
    
     
        
    # print('all_bank_balance: ', account_balance)
        

    # print('Bank: ' , num_bank_accounts)
    
    num_simple_accounts = Account.objects.filter(operator__exact = request.user).filter(book__exact = '1').count()

    num_hawala_accounts = Account.objects.filter(operator__exact = request.user).filter(book__exact = '3').count()
    
    num_clearing_accounts = Account.objects.filter(operator__exact = request.user).filter(book__exact = '2').count()

    num_lahore_accounts = Account.objects.filter(operator__exact = request.user).filter(book__exact = '5').count()


    num_transactions = Transaction.objects.filter(operator__exact = request.user).count()

    credit = Transaction.objects.filter(operator__exact = request.user).filter(transaction_type__exact='Credit').count()

    debit = Transaction.objects.filter(operator__exact = request.user).filter(transaction_type__exact='Debit').count()

    bank_blnc_list = get_bookAllaccTotal(request, '4')
    cash_blnc_list = get_bookAllaccTotal(request, '6')
    hawala_blnc_list = get_bookAllaccTotal(request, '3')
    clearing_blnc_list = get_bookAllaccTotal(request, '2')
    context = {

        'num_books': num_books,
        'num_accounts':num_accounts,
        'num_bank_accounts':num_bank_accounts,
        'num_transactions': num_transactions,
        'credit':credit,
        'debit':debit,
        'num_simple_accounts': num_simple_accounts,
        'num_clearing_accounts': num_clearing_accounts,
        'num_hawala_accounts': num_hawala_accounts,
        'num_lahore_accounts':num_lahore_accounts,
        'all_bank_balance':bank_blnc_list,
        'cash_blnc_list':cash_blnc_list,
        'hawala_blnc_list':hawala_blnc_list,
        'clearing_blnc_list':clearing_blnc_list
        

    }

    return render(request, 'home/index.html', context = context)


@login_required
def book_list(request):

    all_books = AccountsBook.objects.filter(operator__exact = request.user).all()

    

    return render(request, 'list_views/book_list.html' ,{
        'all_books': all_books
    })
@login_required
def book_detail(request, id):
        try:
            book = AccountsBook.objects.filter(operator__exact = request.user).get(pk = id)
            book_type = book.book_type
           
        except Account.DoesNotExist:
            raise Http404('Book does not exist')
        
        type = Account.objects.filter(operator__exact = request.user).filter(book__exact = book_type)

        return render(request, 'detail_views/book_detail.html', context={
            'book': book, 
            'type':type
        })

@login_required
def account_list(request):

    all_accounts = Account.objects.filter(operator__exact = request.user).all()

    total_query = 0

    return render(request, 'list_views/account_list.html' ,{
        'all_accounts': all_accounts
    })
@login_required
def accounts_detail(request, id):
        
        try:
            account = Account.objects.filter(operator__exact = request.user).get(pk = id)
            trans1 = account.from_account.filter(operator__exact = request.user).all()
            trans2 = account.to_account.filter(operator__exact = request.user).all()
            account_balance = 0
           
            # print('Trans1: ', trans1)
            # print('Trans2: ', trans2)

            transactions = trans1 | trans2
            


            
            my_list = []
            for transaction in transactions:

                # print('Transaction:', transaction.account, transaction.bank, transaction )
                #Executed when new account is created 
                if transaction.transaction_type == DEBIT and  transaction.account == account and  transaction.bank == None:
                    account_balance = account_balance + transaction.amount
                    my_list.append(account_balance)
                     
                    # print('Debit 1: ', account_balance) 
                
                #Executed when new account is created 
                if transaction.transaction_type == CREDIT and  transaction.account == account and  transaction.bank == None:
                    account_balance = account_balance - transaction.amount

                    my_list.append(account_balance)
                    # print('Credited 2: ', account_balance)



                #Executed when the current account is Credit account and transaction list is debited 
                if transaction.transaction_type == DEBIT and  transaction.account == account and  transaction.bank != None:
                    account_balance = account_balance - transaction.amount
                    my_list.append(account_balance)
                    # print('Debit 2: ', account_balance)
                
                #Executed when the current account is Credit account and transaction list is credited
                if transaction.transaction_type == CREDIT and  transaction.account == account and  transaction.bank != None:
                    account_balance = account_balance - transaction.amount
                    my_list.append(account_balance)
                    # print('Credited 1: ', account_balance)
                
                 #Executed when the current account is Credit account and transaction list is None
                if transaction.transaction_type == NONE and  transaction.account == account and  transaction.bank != None:
                    account_balance = account_balance - transaction.amount
                    my_list.append(account_balance)
                    # print('None 1: ', account_balance)
                
                
                

                
                #Executed when the current account is Debit account and transaction list is debited
                if transaction.transaction_type == DEBIT and  transaction.bank == account and  transaction.bank != None:
                    account_balance = account_balance + transaction.amount
                    my_list.append(account_balance)
                    # print('Debited 3: ', account_balance)
                
                #Executed when the current account is Debit account and transaction list is credited
                if transaction.transaction_type == CREDIT and  transaction.bank == account and  transaction.bank != None:
                    account_balance = account_balance + transaction.amount
                    my_list.append(account_balance)
                    # print('Credited 3: ', account_balance)
                
                #Executed when the current account is Debit account and transaction list is None
                if transaction.transaction_type == NONE and  transaction.bank == account and  transaction.bank != None:
                    account_balance = account_balance + transaction.amount
                    my_list.append(account_balance)
                    # print('None 2: ', account_balance)
                
            zipped_lists = zip(transactions, my_list)

            

                   
        except Account.DoesNotExist:
            raise Http404('Book does not exist')
        
        return render(request, 'detail_views/account_detail.html', context={
            'account': account, 
            'transactions':transactions,
            'clearing' : CLEARING,
            'simple' : SIMPLE,
            'credit': CREDIT,
            'debit': DEBIT,
            'list': zipped_lists,
            'none':None,
            'id':id,
            'my_list':str(my_list)   
        })








@login_required
def transaction_list(request):
    print("This is Transaction List")
    try:
        
        transaction_list = Transaction.objects.filter(operator__exact = request.user).all().order_by('id')
        banks = Account.objects.filter(operator__exact = request.user).filter(book__exact = '4').all()
        cash_accounts = Account.objects.filter(operator__exact = request.user).filter(book__exact = '6').all()
        if transaction_list:
            for trans in transaction_list:
                print("trans:", trans)
            balance_list=[]
            balance=0
            total_balance = 0
            total_bank_balance = 0
            total_cash= 0
            total_credit = 0
            total_debit = 0
            total_hawala = 0
            total_clearing = 0
            
            TotalCredit = Transaction.objects.filter(operator__exact = request.user).filter(transaction_type__exact = CREDIT).aggregate(Sum('amount')).get('amount__sum')
            # print('CreditQuery: ', TotalCredit, type(TotalCredit))
            accounts_clearing = Account.objects.filter(operator__exact = request.user).filter(book__exact = '2').all()
            accounts_hawala = Account.objects.filter(operator__exact = request.user).filter(book__exact = '3').all()

            if accounts_clearing:
                for account in accounts_clearing:
                    # print('Bank HhHH', account)
                    # print('Balance', account.balance)
                    total_clearing = total_clearing + account.balance
                # print('Total Clearings', total_clearing)
            
            if accounts_hawala:
                for account in accounts_hawala:
                    # print('Bank', account)
                    # print('Balance', account.balance)
                    total_hawala = total_hawala + account.balance
                # print('Total Hawala', total_hawala)



            transaction_list_credit = Transaction.objects.filter(operator__exact = request.user).filter(transaction_type__exact = CREDIT)
            transaction_list_debit = Transaction.objects.filter(operator__exact = request.user).filter(transaction_type__exact = DEBIT)
           
            if transaction_list_credit:
                for trans in transaction_list_credit:
                    total_credit = total_credit + trans.amount

            if transaction_list_debit:
                for trans in transaction_list_debit:
                    total_debit = total_debit + trans.amount

            if transaction_list:
                for trans in transaction_list:
                    if trans.transaction_type == DEBIT:
                        # print("transaction Debit: ", trans.amount)
                        balance = balance + trans.amount
                        balance_list.append(balance)
                    if trans.transaction_type == CREDIT:
                        # print("transaction Credit: ", trans.amount)
                        balance = balance - trans.amount
                        balance_list.append(balance)
                 
            # for x in balance_list:
            #     print("x: ", x)
                    
            if banks:
                for bank in banks:
                    # print('Bank', bank)
                    # print('Balance', bank.balance)
                    total_bank_balance = total_bank_balance + bank.balance
            
            if cash_accounts:
                for cash in cash_accounts:
                    total_cash = total_cash + cash.balance
            total_bank_balance = total_bank_balance + total_cash   

            # print('Bank: ', total_bank_balance)
            
            

            paginator = Paginator(transaction_list, 25) # Show 25 contacts per page.
            
            page_number = request.GET.get('page', paginator.num_pages )
            try:
                page_obj = paginator.page(page_number)
            except EmptyPage:
                page_obj =  paginator.page(1)
            
            
            zippedList = zip(page_obj, balance_list)
            
            return render(request, 'list_views/transaction_list.html', context={
            #'transaction_list': transaction_list, 
            'total_balance': total_balance,
            'total_bank_balance':total_bank_balance,
            'credit': CREDIT,
            'debit': DEBIT,
            'total_credit': total_credit,
            'total_debit':total_debit, 
            'total_hawala':total_hawala,
            'total_clearing':total_clearing, 
            'page_obj':page_obj,
            'TotalCredit':TotalCredit,
            'balance_list':balance_list,
            'zippedList':zippedList
            
            
            })
        else:
            return render(request, 'list_views/transaction_list.html', context={
            'transaction_list': transaction_list, 
            })

    
    except Account.DoesNotExist:
        raise Http404('Transaction does not exist')
            
    

@login_required
def transaction_detail(request, id):
        
        try:
            transaction = Transaction.objects.filter(operator__exact = request.user).get(pk = id)
            
            print("account: " , transaction)


        except Transaction.DoesNotExist:
            raise Http404('Transactions does not exist')
        
        return render(request, 'detail_views/transaction_detail.html', context={
            'transaction': transaction, 
            
        })



        #Forms

@login_required
def add_book(request):
    book_types = AccountsBook.objects.filter(operator__exact = request.user).all()
    
    
    context = {
        'book_types':book_types,
        'values': request.POST,
        'simple': SIMPLE,
        'clear': CLEARING,
        'hawala': HAWALA,
        'bank': BANK,
        'lahore': LAHORE,
        'cash':CASH,
        'qarz':QARZ,
        'iran':IRAN,
        'gadi_kharcha':GADI_KHARCHA,
        'taftan':TAFTAN
        
    }

    if request.method == 'POST':
        date =  request.POST['date']
        title = request.POST['title']
        type = request.POST['type']
        print('Type: ', type)
        
        if not title: 
            messages.error(request, 'Title is required')
            return render(request, 'all_forms/add_book.html', context = context)
        if not type:
            messages.error(request, 'Type is required')
            return render(request, 'all_forms/add_book.html', context = context)
        
        if not date:
            date = datetime.today()

        AccountsBook.objects.create(operator = request.user , book_title = title,  book_type = type, book_created_date = date)

        messages.success(request, 'Book saved succesfully')

        return redirect('book',)

    if request.method == 'GET':
        return render(request, 'all_forms/add_book.html', context = context)


@login_required
def edit_book(request, id):
    book_types = AccountsBook.objects.filter(operator__exact = request.user).all()
    book = AccountsBook.objects.filter(operator__exact = request.user).get(pk=id)
    book_type = book.book_type
    type = Account.objects.filter(operator__exact = request.user).filter(book__exact = book_type)

    context = {
        'book':book,
        'type':type,
        'book_types':book_types,
        'values': book,
        'simple': SIMPLE,
        'clear': CLEARING,
        'hawala': HAWALA,
        'bank': BANK,
        'lahore': LAHORE,
        'cash':CASH,
        'qarz':QARZ,
        'iran':IRAN,
        'gadi_kharcha':GADI_KHARCHA,
        'taftan':TAFTAN
        
    }

    if request.method == 'POST':
        date =  request.POST['date']
        title = request.POST['title']
        type = request.POST['type']
        print('Type: ', type)
        
        if not title: 
            messages.error(request, 'Title is required')
            return render(request, 'all_forms/edit_book.html', context = context)
        if not type:
            messages.error(request, 'Type is required')
            return render(request, 'all_forms/edit_book.html', context = context)
        
        if not date:
            date = book.book_created_date
        book.book_title = title
        book.book_type = type
        book.book_created_date = date

        book.save(force_update=True)
        messages.success(request, 'Book saved succesfully')

        return redirect('book',)

    if request.method == 'GET':
        return render(request, 'all_forms/edit_book.html', context = context)


@login_required
def add_account(request):
    try:
        books = AccountsBook.objects.filter(operator__exact = request.user).all()
        transactions = Transaction.objects.filter(operator__exact = request.user).all()
        credit = CREDIT
        debit = DEBIT
        reference_number = ''
        trans_balance= 0
        account_balance = 0
    except Account.DoesNotExist:
        messages.error(request, 'Account Does not exist')
        return render(request, 'all_forms/edit_transaction.html')

    
    context = {
        'books' : books,
        'values': request.POST,
        'credit':credit,
        'debit':debit,
        'none':None
    }
    try:
        if request.method == 'POST':
            date = request.POST['date_created']
            title = request.POST['title']
            phone_number = request.POST['phone_number']
            address = request.POST['address']
            amount = request.POST['amount']  
            amount = float(amount)
            book = request.POST['book']
            transaction_type  = request.POST['transaction_type']
            
            if not title: 
                messages.error(request, 'Title is required')
                return render(request, 'all_forms/add_account.html', context = context)
            if not phone_number:
                messages.error(request, 'Phone Number is required')
                return render(request, 'all_forms/add_account.html', context = context)
            if not address:
                messages.error(request, 'Address is required')
                return render(request, 'all_forms/add_account.html', context = context)
            if not book:
                messages.error(request, 'Book is required')
                return render(request, 'all_forms/add_account.html', context = context)
            if not transaction_type:
                messages.error(request, 'Types is required')
                return render(request, 'all_forms/add_account.html', context = context)
            
            reference_number = title 
            
            
            
            if transaction_type == debit:
                account_balance = account_balance + amount
                
            if transaction_type == credit:
                account_balance = account_balance - amount
            
            if transactions:
                for trans in transactions:
                    if reference_number == trans.refernce_number:
                        messages.error(request, 'Reference Number already exist')
                        return render(request, 'all_forms/add_account.html', context = context)
    

            if not date:
                date = datetime.today()
            
            account =  Account.objects.create(operator = request.user ,date_created=date, title = title, phone_number = phone_number, address = address , amount= float(amount), transaction_type = transaction_type, book=book, balance = account_balance)
       
        
            if transactions:
                for trans in transactions:
                    trans_balance =trans.balance_after_transaction
                
        

    
            if transaction_type == CREDIT:
                trans_balance = trans_balance - amount
            
            elif transaction_type == DEBIT:
                trans_balance = trans_balance + amount
            else:
                trans_balance = trans_balance
        

            Transaction.objects.create(operator = request.user , transaction_date =date, refernce_number =  reference_number, transaction_detail ='Opening Balance',account= account, bank = None, transaction_type = transaction_type, amount = float(amount), slip = '' , balance_after_transaction = trans_balance)

            
            messages.success(request, 'Account saved succesfully')

            return redirect('account',)
    except:
        messages.error(request, 'Fill the form fully')
        return render(request, 'all_forms/edit_transaction.html',context = context)

    if request.method == 'GET':
        return render(request, 'all_forms/add_account.html', context = context)


@login_required
def add_transaction(request):
    transaction_list = Transaction.objects.filter(operator__exact = request.user).all()
    accounts = Account.objects.filter(operator__exact = request.user).all()
    banks = Account.objects.filter(operator__exact = request.user).filter(book__exact = '4').all()
    credit = CREDIT
    debit = DEBIT
    last_transaction_total = 0
    last_transaction_date = ''

    
    context = {
        'accounts' : accounts,
        'banks':banks,
        'credit':credit,
        'debit': debit,
        'none': NONE,
        'values': request.POST,
    }

    try:
        if request.method == 'POST':
            transaction_date = request.POST['transaction_date']
            print('Transaction:', transaction_date)
            transaction_detail = request.POST['transaction_detail']
            refernce_number = request.POST['refernce_number']
            account = request.POST['account']
            print('Account: ', account)
            account_object = Account.objects.filter(operator__exact = request.user).get(pk = account)
            bank = request.POST['bank']
            bank_object = Account.objects.filter(operator__exact = request.user).get(pk = bank)
            transaction_type = request.POST['transaction_type']
            amount = request.POST['amount']
            
            
            slip = request.FILES.get('slip')
            uploaded_file_url = ''
            if slip:
                fs = FileSystemStorage()
                filename = fs.save(slip.name, slip)
                uploaded_file_url = fs.url(filename)
            
            print('Slip:',slip)

            if transaction_list:
                for transaction in  transaction_list:
                    last_transaction_date = transaction.transaction_date
                    last_transaction_total = transaction.balance_after_transaction
                    if refernce_number == transaction.refernce_number:
                        messages.error(request, 'Reference Number already exist')
                        return render(request, 'all_forms/add_transaction.html', context = context)
                print('last date: ', last_transaction_date, type(last_transaction_date))
                print('curent date: ', transaction_date, type(transaction_date))
                if not transaction_date:
                    transaction_date = datetime.today()
                    transaction_date = transaction_date.date()
                    transaction_date = str(transaction_date)
                 #changes needed to be done in production   
                last_transaction_date = last_transaction_date.strftime('%Y-%m-%d')
                last_transaction_date = datetime.strptime(last_transaction_date, '%Y-%m-%d')                
                current_date = datetime.strptime(transaction_date, '%Y-%m-%d')

                print('last date: ', last_transaction_date, type(last_transaction_date))

                print('curent date: ', current_date, type(current_date))
                current_date = pytz.utc.localize(current_date)
                last_transaction_date = pytz.utc.localize(last_transaction_date)
                #changes needed to be done in production  
                if current_date < last_transaction_date:
                    messages.success(request, 'Date must be greater than last transaction date')
                    return redirect('add-transaction')


            
            
            # if transaction_type == CREDIT:
            #     account_object.balance = account_object.balance - float(amount)
            #     bank_object.balance = bank_object.balance +  float(amount)
            #     last_transaction_total = last_transaction_total - float(amount)
                

            
            # if transaction_type == DEBIT:
            #     account_object.balance = account_object.balance - float(amount)
            #     bank_object.balance = bank_object.balance +  float(amount)
            #     last_transaction_total = last_transaction_total + float(amount)
            
            # if transaction_type == NONE:
            #     account_object.balance = account_object.balance - float(amount)
            #     bank_object.balance = bank_object.balance +  float(amount)
            #     last_transaction_total = last_transaction_total
            

            if not transaction_date:
                transaction_date = datetime.today()
            

            if not refernce_number:
                refernce_number = 'None'
            if not transaction_type:
                transaction_type = None
           
        
            if not uploaded_file_url:
                uploaded_file_url = ''
            
            if bank_object == account_object:
                messages.success(request, 'Credit and Debit accounts can not be same!')
                return redirect('add-transaction')

                
            

            print('Account Balance: ',account_object.balance)
            print('Bank Balance: ',bank_object.balance)

            account_object.save(force_update=True)
            bank_object.save(force_update=True)
            
            Transaction.objects.create(operator = request.user , transaction_date = transaction_date, refernce_number = refernce_number ,transaction_detail =transaction_detail,account= account_object, bank =bank_object, transaction_type =transaction_type, amount = amount, slip = uploaded_file_url , balance_after_transaction = last_transaction_total)
            messages.success(request, 'Transaction saved succesfully')
            return redirect('transaction')      
    
    except Account.DoesNotExist:
        e = sys.exc_info()  
        messages.error(request, 'Error')
        return render(request, 'all_forms/add_transaction.html', context = context)
                

    if request.method == 'GET':
        return render(request, 'all_forms/add_transaction.html', context = context)

    

@login_required
def edit_transaction(request, id):

#try:
    transaction_list = Transaction.objects.filter(operator__exact = request.user).all()
    transaction = Transaction.objects.filter(operator__exact = request.user).get(pk = id)
    accounts = Account.objects.filter(operator__exact = request.user).all()
    last_transaction_total= 0
    last_total = 0
    flag = 0
    account_trans_count=0


    context = {
        'all_accounts':accounts,
        'transaction': transaction,
        'values':transaction,
        'credit':CREDIT,
        'debit':DEBIT,
        'none':NONE
    
    }

    if request.method == 'POST':

        # if transaction.account:
        #     transaction.account.balance = transaction.account.balance + transaction.amount
        #     transaction.account.save()
        # if transaction.bank:
        #     transaction.bank.balance = transaction.bank.balance - transaction.amount
        #     transaction.bank.save()
        # if transaction.transaction_type == CREDIT:
        #     transaction.balance_after_transaction = transaction.balance_after_transaction + transaction.amount
        #     transaction.save()
        # if transaction.transaction_type == DEBIT:
        #     transaction.balance_after_transaction = transaction.balance_after_transaction - transaction.amount
        #     transaction.save()
        # if transaction.transaction_type == NONE:
        #     transaction.balance_after_transaction = transaction.balance_after_transaction
        #     transaction.save()
        transaction_date = request.POST['transaction_date']
        transaction_detail = request.POST['transaction_detail']
        refernce_number = request.POST['refernce_number']
        account = request.POST['account']
        account_object = Account.objects.filter(operator__exact = request.user).get(pk = account)
        bank = request.POST['bank']
        if bank:
            bank_object = Account.objects.filter(operator__exact = request.user).get(pk = bank) 
            if bank_object == account_object:
                messages.success(request, 'Credit and Debit accounts can not be same!')
                return redirect('add-transaction')   
        transaction_type = request.POST['transaction_type']
        amount = request.POST['amount'] 
        amount = float(amount)
        
        slip = request.FILES.get('slip')
        uploaded_file_url = ''
        if slip:
            fs = FileSystemStorage()
            filename = fs.save(slip.name, slip)
            uploaded_file_url = fs.url(filename)
        

        print('bank: ', bank)
        print('account balance before : ', account_object.balance)
        
        # if bank == '':
        #     for trans in transaction_list:
        #         print('Tranacrdfd:', trans)
        #         if trans == transaction:
        #             account_trans_count1 = Transaction.objects.filter(operator__exact = request.user).filter(account__exact = account_object).count()
        #             account_trans_count2 = Transaction.objects.filter(operator__exact = request.user).filter(bank__exact = account_object).count()
        #             account_trans_count = account_trans_count1 + account_trans_count2
        #             print('Acc: ',account_trans_count)
        #             if account_trans_count == 1:
        #                 flag = 1                                 
        #                 account_object.balance = 0      
        #                 if transaction_type == CREDIT:
        #                     account_object.balance = account_object.balance - amount
        #                     transaction.balance_after_transaction = last_transaction_total - amount
        #                 if transaction_type == DEBIT:
        #                     account_object.balance = account_object.balance + amount
        #                     transaction.balance_after_transaction = last_transaction_total + amount
        #                 if transaction_type == NONE:
        #                     account_object.balance = account_object.balance + amount
        #                     transaction.balance_after_transaction = last_transaction_total 
                        
        #                 transaction.save(force_update=True)
        #                 account_object.save(force_update=True)
        #             else:
        #                 messages.success(request, 'Transaction cannot be updated')
        #                 return redirect('transaction')        
        #         else:
        #             if account_trans_count == 1:
        #                 last_transaction_total = trans.balance_after_transaction
        #                 print('account balance after else : ', account_object.balance)
        #             else:
        #                 messages.success(request, 'Transaction cannot be updated')
        #                 return redirect('transaction',)
        
        # else:
        #     flag = 1  
        #     for trans in transaction_list:
        #         if trans == transaction:                            
        #             if transaction_type == CREDIT:
        #                 transaction.balance_after_transaction = last_transaction_total - amount
        #                 transaction.save(force_update=True)
        #             if transaction_type == DEBIT:
        #                 transaction.balance_after_transaction = last_transaction_total + amount
        #                 transaction.save(force_update=True)
        #             if transaction_type == NONE:
        #                 transaction.balance_after_transaction = last_transaction_total 
        #                 transaction.save(force_update=True)
        #             account_object.balance = account_object.balance - amount
        #             bank_object.balance = bank_object.balance + amount

        #             transaction.save(force_update=True)
        #             account_object.save(force_update=True)
        #             bank_object.save(force_update=True)
        #             print("transaction q12213", transaction.balance_after_transaction)
        #         else:
        #             last_transaction_total = trans.balance_after_transaction
        #             transaction.save(force_update=True)
            

        # if flag == 1:
        #     for trans in transaction_list:
        #         if trans == transaction:
        #             if transaction_type == CREDIT:
        #                 trans.balance_after_transaction = last_total - amount
        #                 last_total = trans.balance_after_transaction
        #                 print("T C Last Balnc: ",last_total)
        #             if transaction_type == DEBIT:
        #                 trans.balance_after_transaction = last_total + amount
        #                 last_total = trans.balance_after_transaction
        #                 print("T D Last Balnc: ",last_total)
        #             if transaction_type == NONE:
        #                 trans.balance_after_transaction = last_total
        #                 last_total = trans.balance_after_transaction
        #                 print("T N Last Balnc: ",last_total)
        #             trans.save(force_update=True)
        #         else:
        #             if trans.transaction_type == CREDIT:
        #                 trans.balance_after_transaction = last_total - trans.amount
        #                 last_total = trans.balance_after_transaction
        #                 print("C Last Balnc: ",last_total)
        #             if trans.transaction_type == DEBIT:
        #                 trans.balance_after_transaction = last_total + trans.amount
        #                 last_total = trans.balance_after_transaction
        #                 print("D Last Balnc: ",last_total)
        #             if trans.transaction_type == NONE:
        #                 trans.balance_after_transaction = last_total
        #                 last_total = trans.balance_after_transaction
        #                 print("N Last Balnc: ",last_total)
        #             trans.save(force_update=True)
        #     flag = 0




        if not transaction_date:
            transaction_date = transaction.transaction_date
        

        if transaction.operator == request.user:
            if transaction.transaction_date != transaction_date:
                transaction.transaction_date = transaction_date
            if transaction.refernce_number != refernce_number:
                transaction.refernce_number = refernce_number
            if transaction.transaction_detail != transaction_detail:
                transaction.transaction_detail = transaction_detail
            if transaction.account != account_object:
                transaction.account= account_object
            if bank:
                if transaction.bank != bank_object:
                    transaction.bank = bank_object
            if transaction.transaction_type != transaction_type:
                transaction.transaction_type =transaction_type
            if  transaction.amount != amount:
                transaction.amount = amount 
            if transaction.slip != uploaded_file_url:
                transaction.slip = uploaded_file_url  
            #if transaction.balance_after_transaction != last_transaction_total:
            transaction.balance_after_transaction  = transaction.balance_after_transaction              
            
            transaction.save(force_update=True)


        messages.success(request, 'Transaction updated succesfully')

        return redirect('transaction',)

#except:
 #   e = sys.exc_info() 
 #   messages.error(request, 'Some fields are empty')
 #   return render(request, 'all_forms/edit_transaction.html', context = context)
            
    
    if request.method == 'GET':
        return render(request, 'all_forms/edit_transaction.html', context = context)
    

@login_required
def delete_transaction(request, id):
    transaction = Transaction.objects.filter(operator__exact = request.user).get(pk = id)
    transaction.delete()
    messages.success(request, 'Transaction deleted succesfully')

    return redirect('transaction',)



    

@login_required   
def search_results(request):
    if request.method == 'GET':
        search_value = request.GET['search']
        #search_account = Account.objects.filter(operator__exact = request.user).get(title__icontains = search_value)

       # search1 = Transaction.objects.filter(operator__exact = request.user).filter(account__icontains=search_account)
        #search2= Transaction.objects.filter(operator__exact = request.user).filter(bank__icontains=search_account)
        search3= Transaction.objects.filter(operator__exact = request.user).filter(refernce_number__icontains=search_value)
        search4= Transaction.objects.filter(operator__exact = request.user).filter(amount__icontains=search_value)

        search_result =  search3 | search4

    return render(request, 'search/search.html', {
        'search_result': search_result
    })


@login_required   
def date_range(request):
    if request.method == 'POST':
        start = request.POST['start']
        end = request.POST['end']
        balance_list = []
        range_balance_list = []
        balance = 0
        zippedlist = 0
        strdbdate= 0
        dbdate = 0 
        sdate = 0
        edate = 0
        print('start: ',start , type(start) )
        start_obj = dt.strptime(start, "%m/%d/%Y")
        start = start_obj.strftime("%Y-%m-%d")
        end_obj = dt.strptime(end, "%m/%d/%Y")
        end = end_obj.strftime("%Y-%m-%d")
        print('start obj: ',start_obj , type(start_obj) )
        date_range_result = Transaction.objects.filter(operator__exact = request.user).filter(transaction_date__range = [start_obj, end_obj])  
        transaction_list = Transaction.objects.filter(operator__exact = request.user).all().order_by('id')
        print("start", start)
        print("end", end)
        if transaction_list:
                for trans in transaction_list:
                    if trans.transaction_type == DEBIT:
                        # print("transaction Debit: ", trans.amount)
                        balance = balance + trans.amount
                        balance_list.append(balance)
                        # print("Date: ", trans.transaction_date, type(trans.transaction_date) )
                    if trans.transaction_type == CREDIT:
                        # print("transaction Credit: ", trans.amount)
                        balance = balance - trans.amount
                        balance_list.append(balance)
        for trans, blanc in zip(transaction_list,balance_list):
            # dbdate = str(trans.transaction_date.date)
            strdbdate = trans.transaction_date.strftime('%Y-%m-%d')
            # print("strdbdate", strdbdate, type(strdbdate))
            dbdate = dt.strptime(strdbdate, "%Y-%m-%d")
            sdate = dt.strptime(start, "%Y-%m-%d")
            edate = dt.strptime(end, "%Y-%m-%d")
            # print("dbdate", dbdate, type(dbdate))
            # print("sdate", sdate, type(sdate))
            # print("edate", edate, type(edate))
            if dbdate >= sdate and  dbdate <= edate:
                print('balnce:', trans, blanc)
                range_balance_list.append(blanc)

                

        # print('Start: ', (start))
        # print('End: ',end )   
        zippedlist =  zip(range_balance_list,date_range_result)   
        print('End:' )    
    return render(request, 'search/date_range.html', {
       'zippedlist':zippedlist,
       'date_range_result':date_range_result,
       'start':start,
       'end':end,
       'credit': CREDIT,
        'debit': DEBIT,
        'range_balance_list':range_balance_list
        
    })

def date_range_account(request, id):
    
    try:
        if request.method == 'POST':
            start = request.POST['start']
            end = request.POST['end']
            zipped_lists = []
            total_credit = 0
            total_debit = 0
            account_balance = 0
            total_credit = 0
            total_debit = 0
            balance_list = []
            range_balance_list = []
            strdbdate = ''
            start_obj = dt.strptime(start, "%m/%d/%Y")
            start = start_obj.strftime("%Y-%m-%d")
            end_obj = dt.strptime(end, "%m/%d/%Y")
            end = end_obj.strftime("%Y-%m-%d")
            
            account = Account.objects.filter(operator__exact = request.user).get(pk = id)
            
            trans1 = account.from_account.filter(operator__exact = request.user).all()
            trans2 = account.to_account.filter(operator__exact = request.user).all()        
            transactions = trans1 | trans2

            fTDRange = account.from_account.filter(operator__exact = request.user).filter(transaction_date__range = [start, end]) 
            tTDRange = account.to_account.filter(operator__exact = request.user).filter(transaction_date__range = [start, end])        
            aTDRange = fTDRange | tTDRange

            if aTDRange:
                for tran in aTDRange:
                    print("tran: ", tran.amount)
            sdate = dt.strptime(start, "%Y-%m-%d")
            edate = dt.strptime(end, "%Y-%m-%d")
            # print("start_date 12", sdate, type(sdate))
            # print("end_date 12", edate, type(edate))
            
            for transaction in transactions:
                if transaction.account == account and transaction.bank == None and transaction.transaction_type == DEBIT:
                    total_debit = total_debit + transaction.amount
                if transaction.bank == account and transaction.account != None:
                    total_debit = total_debit + transaction.amount

                
                if transaction.account == account and transaction.bank == None and transaction.transaction_type == CREDIT:
                    total_credit = total_credit + transaction.amount

                if transaction.account == account and transaction.bank != None:
                    total_credit = total_credit + transaction.amount
            
                

                # print('Transaction:', transaction.account, transaction.bank, transaction )
                #Executed when new account is created 
                if transaction.transaction_type == DEBIT and  transaction.account == account and  transaction.bank == None:
                    account_balance = account_balance + transaction.amount
                    balance_list.append(account_balance)
                    
                    
                    # print('Debit 1: ', account_balance)
                
                #Executed when new account is created 
                if transaction.transaction_type == CREDIT and  transaction.account == account and  transaction.bank == None:
                    account_balance = account_balance - transaction.amount

                    balance_list.append(account_balance)
                    
                    # print('Credited 2: ', account_balance)



                #Executed when the current account is From Account account and transaction list is debited 
                if transaction.transaction_type == DEBIT and  transaction.account == account and  transaction.bank != None:
                    account_balance = account_balance - transaction.amount
                    balance_list.append(account_balance)

                    # print('Debit 2: ', account_balance)
                
                #Executed when the current account is Credit account and transaction list is credited
                if transaction.transaction_type == CREDIT and  transaction.account == account and  transaction.bank != None:
                    account_balance = account_balance - transaction.amount
                    balance_list.append(account_balance)
                    # print('Credited 1: ', account_balance)
                
                    #Executed when the current account is Credit account and transaction list is None
                if transaction.transaction_type == NONE and  transaction.account == account and  transaction.bank != None:
                    account_balance = account_balance - transaction.amount
                    balance_list.append(account_balance)
                    # print('None 1: ', account_balance)
                #Executed when the current account is Debit account and transaction list is None
                if transaction.transaction_type == NONE and  transaction.bank == account and  transaction.account != None:
                    account_balance = account_balance + transaction.amount
                    balance_list.append(account_balance)
                    # print('None 2: ', account_balance)
                
                

                
                #Executed when the current account is Debit account and transaction list is debited
                if transaction.transaction_type == DEBIT and  transaction.bank == account and  transaction.account != None:
                    account_balance = account_balance + transaction.amount
                    balance_list.append(account_balance)

                    # print('Debited 3: ', account_balance)
                
                #Executed when the current account is Debit account and transaction list is credited
                if transaction.transaction_type == CREDIT and  transaction.bank == account and  transaction.bank != None:
                    account_balance = account_balance + transaction.amount
                    balance_list.append(account_balance)
                    # print('Credited 3: ', account_balance)
                
                

            # print('Total Credit: ', total_credit, 'Total Debit: ', total_debit)
            # print('MYList: ', type(my_list), my_list)
            
            # for x in balance_list:
            #     print("Balance: ", x)
            
            for trans, blanc in zip(transactions,balance_list):
                strdbdate = trans.transaction_date.strftime('%Y-%m-%d')
                dbdate = dt.strptime(strdbdate, "%Y-%m-%d")
                if dbdate >= sdate and  dbdate <= edate:
                    # print('balnce:', trans, blanc)
                    range_balance_list.append(blanc)
            
            


            zippedlist =  zip(range_balance_list,aTDRange)   


            return render(request, 'search/date_range_account.html',{
        'start':start,
        'end':end,
        'account': account, 
        'clearing' : CLEARING,
        'simple' : SIMPLE,
        'credit': CREDIT,
        'debit': DEBIT,
        'list': zippedlist,
        'none':None,
        'total_credit': total_credit,
        'total_debit':total_debit,
        'aTDRange':aTDRange,
        'id':id,
        'range_balance_list':range_balance_list
            
        })

            # response = HttpResponse(content_type = 'application/pdf')
            # response['Content-Dispostion'] = 'inline; attachment; filename = Tranasction'+\
            # str(datetime.now()) + '.pdf'
            # response['Content-Transfer-Encoding'] = "binary"


            # htmlstring =  render_to_string('search/account_pdf.html', {
            #         'start':start_date,
            #         'end':end_date,
            #         'account': account, 
            #         'transactions':transactions,
            #         'clearing' : CLEARING,
            #         'simple' : SIMPLE,
            #         'credit': CREDIT,
            #         'debit': DEBIT,
            #         'list': zipped_lists,
            #         'none':None,   
            #         'Campany_name': request.user.first_name,
            #         'tagline': request.user.last_name,
            #         'total_credit': total_credit,
            #         'total_debit':total_debit
           
            #         })
            # html = HTML(string = htmlstring)
            # result = html.write_pdf()

            # with tempfile.NamedTemporaryFile(delete=True) as output:
            #     output.write(result)
            #     output.flush()
            #     output= open(output.name , 'rb')
            #     response.write(output.read())
            # return response
    except: 
        e = sys.exc_info() 
        print(e)
        # messages.error(request, 'Error')
        return render(request, 'search/date_range_account.html')

    

def acc_export_pdf(request,id, start, end):
    zipped_lists = []
    total_credit = 0
    total_debit = 0
    account_balance = 0
    total_credit = 0
    total_debit = 0
    balance_list = []
    range_balance_list = []
    strdbdate = ''

    
    account = Account.objects.filter(operator__exact = request.user).get(pk = id)
    
    trans1 = account.from_account.filter(operator__exact = request.user).all()
    trans2 = account.to_account.filter(operator__exact = request.user).all()        
    transactions = trans1 | trans2

    fTDRange = account.from_account.filter(operator__exact = request.user).filter(transaction_date__range = [start, end]) 
    tTDRange = account.to_account.filter(operator__exact = request.user).filter(transaction_date__range = [start, end])        
    aTDRange = fTDRange | tTDRange

    if aTDRange:
        for tran in aTDRange:
            print("tran: ", tran.amount)
    sdate = dt.strptime(start, "%Y-%m-%d")
    edate = dt.strptime(end, "%Y-%m-%d")
    # print("start_date 12", sdate, type(sdate))
    # print("end_date 12", edate, type(edate))
    
    for transaction in transactions:
        if transaction.account == account and transaction.bank == None and transaction.transaction_type == DEBIT:
            total_debit = total_debit + transaction.amount
        if transaction.bank == account and transaction.account != None:
            total_debit = total_debit + transaction.amount

        
        if transaction.account == account and transaction.bank == None and transaction.transaction_type == CREDIT:
            total_credit = total_credit + transaction.amount

        if transaction.account == account and transaction.bank != None:
            total_credit = total_credit + transaction.amount
    
        

        # print('Transaction:', transaction.account, transaction.bank, transaction )
        #Executed when new account is created 
        if transaction.transaction_type == DEBIT and  transaction.account == account and  transaction.bank == None:
            account_balance = account_balance + transaction.amount
            balance_list.append(account_balance)
            
            
            # print('Debit 1: ', account_balance)
        
        #Executed when new account is created 
        if transaction.transaction_type == CREDIT and  transaction.account == account and  transaction.bank == None:
            account_balance = account_balance - transaction.amount

            balance_list.append(account_balance)
            
            # print('Credited 2: ', account_balance)



        #Executed when the current account is From Account account and transaction list is debited 
        if transaction.transaction_type == DEBIT and  transaction.account == account and  transaction.bank != None:
            account_balance = account_balance - transaction.amount
            balance_list.append(account_balance)

            # print('Debit 2: ', account_balance)
        
        #Executed when the current account is Credit account and transaction list is credited
        if transaction.transaction_type == CREDIT and  transaction.account == account and  transaction.bank != None:
            account_balance = account_balance - transaction.amount
            balance_list.append(account_balance)
            # print('Credited 1: ', account_balance)
        
            #Executed when the current account is Credit account and transaction list is None
        if transaction.transaction_type == NONE and  transaction.account == account and  transaction.bank != None:
            account_balance = account_balance - transaction.amount
            balance_list.append(account_balance)
            # print('None 1: ', account_balance)
        #Executed when the current account is Debit account and transaction list is None
        if transaction.transaction_type == NONE and  transaction.bank == account and  transaction.account != None:
            account_balance = account_balance + transaction.amount
            balance_list.append(account_balance)
            # print('None 2: ', account_balance)
        
        

        
        #Executed when the current account is Debit account and transaction list is debited
        if transaction.transaction_type == DEBIT and  transaction.bank == account and  transaction.account != None:
            account_balance = account_balance + transaction.amount
            balance_list.append(account_balance)

            # print('Debited 3: ', account_balance)
        
        #Executed when the current account is Debit account and transaction list is credited
        if transaction.transaction_type == CREDIT and  transaction.bank == account and  transaction.bank != None:
            account_balance = account_balance + transaction.amount
            balance_list.append(account_balance)
            # print('Credited 3: ', account_balance)
        
        

    # print('Total Credit: ', total_credit, 'Total Debit: ', total_debit)
    # print('MYList: ', type(my_list), my_list)
    
    # for x in balance_list:
    #     print("Balance: ", x)
    
    for trans, blanc in zip(transactions,balance_list):
        strdbdate = trans.transaction_date.strftime('%Y-%m-%d')
        dbdate = dt.strptime(strdbdate, "%Y-%m-%d")
        if dbdate >= sdate and  dbdate <= edate:
            # print('balnce:', trans, blanc)
            range_balance_list.append(blanc)
    
    


    zippedlist =  zip(range_balance_list,aTDRange)   
 
    response = HttpResponse(content_type = 'application/pdf')
    response['Content-Dispostion'] = 'inline; attachment; filename = Tranasction'+\
        str(datetime.now()) + '.pdf'
    response['Content-Transfer-Encoding'] = "binary"
    html_string = render_to_string('search/account_pdf.html', {
        'start':start,
    'end':end,
    'account': account, 
    'clearing' : CLEARING,
    'simple' : SIMPLE,
    'credit': CREDIT,
    'debit': DEBIT,
    'list': zippedlist,
    'none':None,
    'total_credit': total_credit,
    'total_debit':total_debit,
    'aTDRange':aTDRange

        })
    html = HTML(string = html_string)
    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output= open(output.name , 'rb')
        response.write(output.read())
    return response


def export_pdf(request, start, end):
    date_range_result = Transaction.objects.filter(operator__exact = request.user).filter(transaction_date__range = [start, end])  
    response = HttpResponse(content_type = 'application/pdf')
    response['Content-Dispostion'] = 'inline; attachment; filename = Tranasction'+\
        str(datetime.now()) + '.pdf'
    response['Content-Transfer-Encoding'] = "binary"
    html_string = render_to_string('search/pdf_export.html', {
        'transaction_list': date_range_result,
        'start':start,
        'end':end,
        'credit': CREDIT,
        'debit': DEBIT,

        })
    html = HTML(string = html_string)
    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output= open(output.name , 'rb')
        response.write(output.read())
    return response




    