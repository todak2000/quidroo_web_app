from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('seller_signup',views.seller_signup, name='seller_signup'),
    path('signin',views.signin, name='signin'),
    path('login_page',views.login_page, name='login_page'),
    path('forgot_page',views.forgot_page, name='forgot_page'),
    path('vendor_signup',views.vendor_signup, name='vendor_signup'),
    path('investor_company_signup',views.investor_company_signup, name='investor_company_signup'),
    path('investor_individual_signup',views.investor_individual_signup, name='investor_individual_signup'),
    path('verify/<token>',views.verify_email),

    path('dashboard',views.dashboard_page, name='dashboard'),
    path('wallet',views.wallet_page, name='wallet'),
    path('invoices',views.invoices_page, name='invoices'),
    path('stats',views.stats_page, name='stats'),
    path('logout',views.logout_page, name='logout'),
]