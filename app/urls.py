from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('seller_signup',views.seller_signup, name='seller_signup'),
    path('signin',views.signin, name='signin'),
    path('login_page',views.login_page, name='login_page'),
    path('forgot_page',views.forgot_page, name='forgot_page'),
    path('upload',views.upload_page, name='upload'),
    path('vendor_signup',views.vendor_signup, name='vendor_signup'),
    path('investor_company_signup',views.investor_company_signup, name='investor_company_signup'),
    path('investor_individual_signup',views.investor_individual_signup, name='investor_individual_signup'),
    path('verify/<token>',views.verify_email),

    path('dashboard',views.dashboard_page, name='dashboard'),
    path('verification',views.verification_page, name='verification'),
    path('wallet',views.wallet_page, name='wallet'),
    path('profile',views.profile_page, name='profile'),
    path('invoices',views.invoices_page, name='invoices'),
    path('bids',views.bids_page, name='bids'),
    path('stats',views.stats_page, name='stats'),
    path('logout',views.logout_page, name='logout'),

    path('withdraw',views.withdraw, name='withdraw'),
    path('topup',views.topup, name='topup'),
    path('makebid',views.makebid, name='makebid'),
    path('editbid',views.editbid, name='editbid'),
    path('upload_invoice',views.upload_invoice, name='upload_invoice'),
    path('invoice_search',views.invoice_search, name='invoice_search'),
    path('purchase_invoice_search',views.purchase_invoice_search, name='purchase_invoice_search'),
    path('invoice_details',views.invoice_details, name='invoice_details'),
    path('bid_details',views.bid_details, name='bid_details'),
    path('fund',views.topup, name='fund'),
    path('upload_verification_data',views.upload_verification_data, name='upload_verification_data'),

    # ADMIN
    path('admin_dashboard',views.admin_dashboard_page, name='admin_dashboard'),
    path('approve_invoice',views.approve_invoice, name='approve_invoice'),
    path('admin_invoice_bids',views.admin_invoice_bids, name='admin_invoice_bids'),
    path('close_bids',views.close_bids, name='close_bids'),
    path('pay_investors',views.pay_investors, name='pay_investors'),
    path('admin_sellers',views.admin_sellers, name='admin_sellers'),
    path('admin_payment',views.admin_payment, name='admin_payment'),
    path('admin_investors',views.admin_investors, name='admin_investors'),
    path('verify_seller',views.verify_seller, name='verify_seller'),
    path('unverify_seller',views.unverify_seller, name='unverify_seller'),
    path('confirm_payment',views.confirm_payment, name='confirm_payment'),
]
