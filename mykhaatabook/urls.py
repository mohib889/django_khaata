from django.urls import path
from . import views

urlpatterns = [
path('', views.index, name='index'),
path('book/', views.book_list, name='book'),
path('book/<int:id>', views.book_detail, name='accountsbook-detail'),
path('account/', views.account_list, name='account'),
path('account/<int:id>', views.accounts_detail, name='account-detail'),
path('transaction/', views.transaction_list, name='transaction'),
path('trans/<int:id>', views.transaction_detail, name='transaction-detail'),
path('add-book/', views.add_book, name='add-book'),
path('edit-book/<int:id>', views.edit_book, name='edit-book'),
path('add-account/', views.add_account, name='add-account'),
path('add-transaction/', views.add_transaction, name='add-transaction'),
path('edit-transaction/<int:id>', views.edit_transaction, name='edit-transaction'),
path('delete-transaction/<int:id>', views.delete_transaction, name='delete-transaction'),
path('search/', views.search_results, name='search_results'),
path('date-range/', views.date_range, name='date_range'),
path('date-range-account/<int:id>/', views.date_range_account, name='date_range_account'),
path("register/", views.register_request, name="register"),
path("login/", views.login_request, name="login"),
path("logout/", views.logout_request, name= "logout"),
path("password_reset/", views.password_reset_request, name="password_reset"),
path("export-pdf/<str:start>/<str:end>", views.export_pdf, name = "export-pdf")
]





