import datetime as DT
import datetime
from hashlib import new
from django.db.models.aggregates import Count, Min
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
import jwt
import json
from django.db.models import Sum, Q, Max
from app.models import (Document, RecentActivity, User, VendorList,Verification, Invoice, Bid, Wallet, Transaction, OnboardingVerification)
from CustomCode import (password_functions, string_generator, validator, credit_score)
from django.core.paginator import Paginator

from quidroo import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.http import JsonResponse

from pysendpulse.pysendpulse import PySendPulse
from decouple import config
import cloudinary.uploader

REST_API_ID = config("REST_API_ID")
REST_API_SECRET = config("REST_API_SECRET")
TOKEN_STORAGE = config("TOKEN_STORAGE")
MEMCACHED_HOST = config("MEMCACHED_HOST")
SPApiProxy = PySendPulse(REST_API_ID, REST_API_SECRET, TOKEN_STORAGE, memcached_host=MEMCACHED_HOST)
sender_email = "donotreply@wastecoin.co"



# Create your views here.
@api_view(["GET"])
def index(request): 
    return render(request,"onboarding/index.html")

@api_view(["GET"])
def login_page(request):
    return render(request,"onboarding/login.html")

# signout api     
def logout_page(request):
    if 'token' in request.session:
        del request.session['token']
    return render(request,"onboarding/login.html") 

@api_view(["GET"])
def forgot_page(request):
    return render(request,"onboarding/forgot_password.html")

# @api_view(["GET"])
# def profile_page(request):
#     return render(request,"seller/profile.html")

@api_view(["GET"])
def profile_page(request):
    try:
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        user_ver = Verification.objects.get(user=user_data)
        return_data = {
            "success": True,
            "status" : 200,
            "activated": user_data.verified,
            "token": request.session['token'],
            "user_id": user_data.user_id,
            "name": user_data.name,
            "company_name": user_data.company_name,
            "role": user_data.role,
            "baseUrl":get_current_site(request).domain,
            "ver_data": user_ver,
            "bank_statement": 'http://'+get_current_site(request).domain+'/media/'+str(user_ver.bank_statement), 
            "cac_certificate": 'http://'+get_current_site(request).domain+'/media/'+str(user_ver.cac_certificate), 
            "idCard": 'http://'+get_current_site(request).domain+'/media/'+str(user_ver.user_Idcard), 
            "avatar": 'http://'+get_current_site(request).domain+'/media/'+str(user_data.avatar_url),
            "user_data": user_data
           
        }
       
        if user_data.role == "seller":
            return render(request,"seller/profile.html", return_data)
            # return render(request,"seller/wallet.html", return_data)
        elif user_data.role == "investor":
            return render(request,"investor/profile.html", return_data)
            # return render(request,"investor/wallet.html", return_data)
        elif user_data.role == "vendor":
            return render(request,"seller/profile.html", return_data)
        else:
            return_data = {
                "success": False,
                "message": "You are not authorized to access this page!",
                "status" : 205,
            }
            return render(request,"onboarding/login.html", return_data)
    except jwt.exceptions.ExpiredSignatureError:
        return_data = {
            "error": "1",
            "message": "Token has expired"
            }
        return render(request,"onboarding/login.html", return_data) 

@api_view(["GET"])
def upload_page(request):
    if 'token' in request.session:
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        vendorList = VendorList.objects.filter(isVerified=True)
        return_data = {
            "success": True,
            "status" : 200,
            "activated": user_data.verified,
            "token": request.session['token'],
            "user_id": user_data.user_id,
            "creditScore":user_data.credit_score,
            "name": user_data.name,
            "company_name": user_data.company_name,
            "role": user_data.role,
            "avatar": 'http://'+get_current_site(request).domain+'/media/'+str(user_data.avatar_url),
            "vendors": vendorList

        }
        if user_data.role == "seller":
            return render(request,"seller/upload.html", return_data)
        else:
            return_data = {
                "success": False,
                "message": "You are not authorized to access this page!",
                "status" : 205,
            }
            return render(request,"onboarding/login.html", return_data) 
    else:
        return_data = {
            "success": False,
            "message": "Sorry! your session expired. Kindly login again",
            "status" : 205,
        }
        return render(request,"onboarding/login.html", return_data)

@api_view(["GET"])
def dashboard_page(request):
    try:
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        wallet_data = Wallet.objects.get(user=user_data)
        local_tx = Transaction.objects.filter(Q(sender_id=user_id) | Q(receiver_id=user_id)).order_by('-created_at')[:3]
        recent_activities = RecentActivity.objects.filter(user_id=user_id).order_by('-date_added')[:3]
        user_ver = Verification.objects.get(user=user_data)
        if user_data.role == "seller":
            # seller dashboard data
            awaitingInvoices = Invoice.objects.filter(seller_id=user_id, invoice_state=0).count()
            confirmedInvoices = Invoice.objects.filter(seller_id=user_id, invoice_state=1).count()
            buyerInvoices = Invoice.objects.filter(seller_id=user_id, invoice_state=2).count()
            soldInvoices = Invoice.objects.filter(seller_id=user_id, invoice_state=3).count()
            completedInvoices = Invoice.objects.filter(seller_id=user_id, invoice_state=4).count()
            totalSold = Invoice.objects.filter(seller_id=user_id, invoice_state=3).aggregate(Sum('invoice_amount'))
            vendors = Invoice.objects.filter(seller_id=user_id).values('vendor_name').distinct().count()
            
            # local_tx = Transaction.objects.filter(Q(sender_id=user_id) | Q(receiver_id=user_id)).order_by('-created_at')[:3]
            
            return_data = {
                "success": True,
                "status" : 200,
                "activated": user_data.verified,
                "message": "Successfull",
                "token": request.session['token'],
                "user_id": user_data.user_id,
                "name": user_data.name,
                "avatar": 'http://'+get_current_site(request).domain+'/media/'+str(user_data.avatar_url),
                "company_name": user_data.company_name,
                "credit_score": user_data.credit_score,
                "role": user_data.role,
                "email":user_data.email,
                "awaiting": awaitingInvoices,
                "confirmed": confirmedInvoices,
                "buyer": buyerInvoices,
                "sold": soldInvoices,
                "vendors":vendors,
                "totalSold":totalSold,
                "completed": completedInvoices,
                "fiat_equivalent":wallet_data.fiat_equivalent,
                "local_transaction": local_tx,
                "recent_activities": recent_activities,
                "awaiting_approval": user_ver.awaiting_approval | False,
                "account_name":user_ver.account_name,
                "account_no": user_ver.account_no,
                "bank": user_ver.bank
            }
            return render(request,"seller/dashboard.html", return_data)
            # return render(request,"seller/wallet.html", return_data)
        elif user_data.role == "investor":
            # buyer dashboard data
            activeBids = Bid.objects.filter(bidder_id=user_data.user_id, invoice__winning_buyer_id="0").count()
            activeBidss = Bid.objects.filter(bidder_id=user_data.user_id, invoice__winning_buyer_id="0")
            purchasedInvoices = Invoice.objects.filter(winning_buyer_id=user_id).count()
            completedInvoices = Invoice.objects.filter(winning_buyer_id=user_id, invoice_state=4).count()
            totalPurchases = Invoice.objects.filter(winning_buyer_id=user_id).aggregate(Sum('receivable_amount'))
            invoices = Invoice.objects.filter(invoice_state=2).order_by('-created_at')[:2]
            noOfInvoices = Invoice.objects.filter(invoice_state=2).count()
            return_data = {
                "success": True,
                "status" : 200,
                "activated": user_data.verified,
                "message": "Successfull",
                "token": request.session['token'],
                "user_id": user_data.user_id,
                "name": user_data.name,
                "now": datetime.date.today(),
                "email":user_data.email,
                "avatar": 'http://'+get_current_site(request).domain+'/media/'+str(user_data.avatar_url),
                "company_name": user_data.company_name,
                "credit_score": user_data.credit_score,
                "role": user_data.role,
                "recent_activities": recent_activities,
                "activeBid": activeBids,
                "activeBidss": activeBidss,
                "purchasedInvoices": purchasedInvoices,
                "completedInvoices":completedInvoices,
                "fiat_equivalent":wallet_data.fiat_equivalent,
                "local_transaction": local_tx,
                "totalPurchases":totalPurchases,
                "invoices":invoices,
                "noOfInvoices":noOfInvoices,
                "account_name":user_ver.account_name,
                "account_no": user_ver.account_no,
                "bank": user_ver.bank
            }
            return render(request,"investor/dashboard.html", return_data)
            # return render(request,"investor/wallet.html", return_data)
        elif user_data.role == "vendor":
            return render(request,"seller/dashboard.html")
        else:
            return_data = {
                "success": False,
                "message": "You are not authorized to access this page!",
                "status" : 205,
            }
            return render(request,"onboarding/login.html", return_data)
    except jwt.exceptions.ExpiredSignatureError:
        return_data = {
            "error": "1",
            "message": "Token has expired"
            }
        return render(request,"onboarding/login.html", return_data)

@api_view(["GET"])
def verification_page(request):
    try:
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        user_ver = Verification.objects.get(user=user_data)

        return_data = {
            "success": True,
            "status" : 200,
            "activated": user_data.verified,
            "token": request.session['token'],
            "user_id": user_data.user_id,
            "name": user_data.name,
            "company_name": user_data.company_name,
            "credit_score": user_data.credit_score,
            "role": user_data.role,
            "avatar": 'http://'+get_current_site(request).domain+'/media/'+str(user_data.avatar_url),
            "awaiting_approval": user_ver.awaiting_approval,
           
        }
        if user_data.role == "seller":
            return render(request,"seller/verification.html", return_data)
            # return render(request,"seller/wallet.html", return_data)
        elif user_data.role == "investor":
            return render(request,"investor/verification.html", return_data)
            # return render(request,"investor/wallet.html", return_data)
        elif user_data.role == "vendor":
            return render(request,"seller/dashboard.html", return_data)
        else:
            return_data = {
                "success": False,
                "message": "You are not authorized to access this page!",
                "status" : 205,
            }
            return render(request,"onboarding/login.html", return_data)
    except jwt.exceptions.ExpiredSignatureError:
        return_data = {
            "error": "1",
            "message": "Token has expired"
            }
        return render(request,"onboarding/login.html", return_data) 
@api_view(["GET"])
def wallet_page(request):
    try:
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        wallet_data = Wallet.objects.get(user=user_data)
        local_tx = Transaction.objects.filter(Q(sender_id=user_id) | Q(receiver_id=user_id)).order_by('-created_at')[:3]
        user_ver = Verification.objects.get(user=user_data)
        return_data = {
            "success": True,
            "status" : 200,
            "activated": user_data.verified,
            "message": "Successfull",
            "token": request.session['token'],
            "user_id": user_data.user_id,
            "company_name": user_data.company_name,
            "role": user_data.role,
            "email":user_data.email,
            "credit_score": user_data.credit_score,
            "name": user_data.name,
            "fiat_equivalent":wallet_data.fiat_equivalent,
            "local_transaction": local_tx,
            "account_name":user_ver.account_name,
            "account_no": user_ver.account_no,
            "avatar": 'http://'+get_current_site(request).domain+'/media/'+str(user_data.avatar_url),
            "bank": user_ver.bank
        }
        if user_data.role == "seller":
            return render(request,"seller/wallet.html", return_data)
        elif user_data.role == "investor":
            return render(request,"investor/wallet.html", return_data)
        elif user_data.role == "vendor":
            return render(request,"seller/wallet.html", return_data)
        else:
            return_data = {
                "success": False,
                "message": "You are not authorized to access this page!",
                "status" : 205,
            }
            return render(request,"onboarding/login.html", return_data) 
    except jwt.exceptions.ExpiredSignatureError:
        return_data = {
            "error": "1",
            "message": "Token has expired"
            }
        return render(request,"onboarding/login.html", return_data)

@api_view(["GET"])
def invoices_page(request):
    # if 'token' in request.session:
    try:
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        # invoices = Invoice.objects.filter(seller_id=user_id).order_by('-created_at')[:10]
        invoices = Invoice.objects.filter(seller_id=user_id).order_by('-created_at')
        invoices2 = Invoice.objects.filter(invoice_state=2).order_by('-created_at')
        noOfInvoices = Invoice.objects.filter(invoice_state=2).count()
        
        if user_data.role == "seller":
            
            num = len(invoices)
            invoiceList = []
            for i in range(0,num):
                due_date = invoices[i].due_date
                additional_details  = invoices[i].additional_details
                invoice_amount  = invoices[i].invoice_amount
                invoice_state = invoices[i].invoice_state
                vendor_name = invoices[i].vendor_name
                invoice_url = invoices[i].invoice_url
                to_json = {
                    "invoice_state": invoice_state,
                    "additional_details": additional_details,
                    "invoice_amount": invoice_amount,
                    "vendor_name": vendor_name,
                    "invoice_url":'http://'+get_current_site(request).domain+'/media/'+str(invoice_url),
                    "due_date": due_date.strftime('%Y-%m-%d')
                }
                invoiceList.append(to_json)
            paginator = Paginator(invoiceList, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return_data = {
                "success": True,
                "status" : 200,
                "activated": user_data.verified,
                "message": "Successfull",
                "name": user_data.name,
                "token": request.session['token'],
                "user_id": user_data.user_id,
                "host":'http://'+get_current_site(request).domain+'/media/',
                "avatar": 'http://'+get_current_site(request).domain+'/media/'+str(user_data.avatar_url),
                "company_name": user_data.company_name,
                "role": user_data.role,
                # "invoices": invoiceList,
                "invoices": page_obj
                # 'page_obj': 
            }
            return render(request,"seller/invoices.html", return_data)
        elif user_data.role == "investor":
            num = len(invoices2)
            invoiceList = []
            if num >0:
                for i in range(0,num):
                    due_date = invoices2[i].due_date
                    id = invoices2[i].id
                    additional_details  = invoices2[i].additional_details
                    invoice_amount  = invoices2[i].invoice_amount
                    invoice_state = invoices2[i].invoice_state
                    receivable_amount = invoices2[i].receivable_amount
                    vendor_name = invoices2[i].vendor_name
                    invoice_url = invoices2[i].invoice_url
                    to_json = {
                        "id":id,
                        "invoice_state": invoice_state,
                        "additional_details": additional_details,
                        "invoice_amount": invoice_amount,
                        "receivable_amount":receivable_amount,
                        "vendor_name": vendor_name,
                        "invoice_url":'http://'+get_current_site(request).domain+'/media/'+str(invoice_url),
                        # "due_date": due_date.strftime('%Y-%m-%d')
                        "due_date": due_date
                    }
                    invoiceList.append(to_json)
                paginator = Paginator(invoiceList, 10)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                return_data = {
                    "success": True,
                    "status" : 200,
                    "activated": user_data.verified,
                    "message": "Successfull",
                    "name": user_data.name,
                    "token": request.session['token'],
                    "user_id": user_data.user_id,
                    "avatar": 'http://'+get_current_site(request).domain+'/media/'+str(user_data.avatar_url),
                    "company_name": user_data.company_name,
                    "role": user_data.role,
                    "invoices": page_obj,
                    "noOfInvoices":noOfInvoices
                }
            else:
                return_data = {
                    "success": True,
                    "status" : 200,
                    "activated": user_data.verified,
                    "message": "Successfull",
                    "name": user_data.name,
                    "token": request.session['token'],
                    "user_id": user_data.user_id,
                    "avatar": 'http://'+get_current_site(request).domain+'/media/'+str(user_data.avatar_url),
                    "company_name": user_data.company_name,
                    "role": user_data.role,
                    "invoices": "no INvoices",
                    "noOfInvoices":noOfInvoices
                }
            
            return render(request,"investor/invoices.html", return_data)
        elif user_data.role == "vendor":
            return render(request,"seller/invoices.html")
        else:
            return_data = {
                "success": False,
                "message": "You are not authorized to access this page!",
                "status" : 205,
            }
            return render(request,"onboarding/login.html", return_data) 
    except jwt.exceptions.ExpiredSignatureError:
        return_data = {
            "error": "1",
            "message": "Token has expired"
            }
        return render(request,"onboarding/login.html", return_data)

@api_view(["GET"])
def bids_page(request):
    # if 'token' in request.session:
    try:
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        activeBids = Bid.objects.filter(bidder_id=user_data.user_id, invoice__winning_buyer_id="0").count()
        activeBidss = Bid.objects.filter(bidder_id=user_data.user_id, invoice__winning_buyer_id="0")
        num = len(activeBidss)
        bidList = []
        for i in range(0,num):
            id= activeBidss[i].id
            due_date = activeBidss[i].invoice.due_date
            additional_details  = activeBidss[i].invoice.additional_details
            invoice_amount  = activeBidss[i].invoice.invoice_amount
            invoice_state = activeBidss[i].invoice.invoice_state
            vendor_name = activeBidss[i].invoice.vendor_name
            invoice_url = activeBidss[i].invoice.invoice_url
            bidder_amount = activeBidss[i].amount
            buyer_ror = activeBidss[i].buyer_ror
            to_json = {
                "invoice_state": invoice_state,
                "additional_details": additional_details,
                "invoice_amount": invoice_amount,
                "vendor_name": vendor_name,
                "buyer_ror":buyer_ror,
                "invoice_url":'http://'+get_current_site(request).domain+'/media/'+str(invoice_url),
                "due_date": due_date,
                "bidder_amount": bidder_amount,
                "id":id
            }
            bidList.append(to_json)
        purchasedInvoicesCount = Invoice.objects.filter(winning_buyer_id=user_id).count()
        purchasedInvoices = Invoice.objects.filter(winning_buyer_id=user_id, invoice_state=3).order_by('-created_at')[:10]
        completedInvoices = Invoice.objects.filter(winning_buyer_id=user_id, invoice_state=4).count()
        totalPurchases = Invoice.objects.filter(winning_buyer_id=user_id, invoice_state=4).aggregate(Sum('receivable_amount'))
        invoices = Invoice.objects.filter(invoice_state=2).order_by('-created_at')[:2]
        noOfInvoices = Invoice.objects.filter(invoice_state=2).count()
        paginator = Paginator(purchasedInvoices, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return_data = {
            "success": True,
            "status" : 200,
            "activated": user_data.verified,
            "message": "Successfull",
            "token": request.session['token'],
            "user_id": user_data.user_id,
            "name": user_data.name,
            "now": datetime.date.today(),
            "avatar": 'http://'+get_current_site(request).domain+'/media/'+str(user_data.avatar_url),
            "company_name": user_data.company_name,
            "credit_score": user_data.credit_score,
            "role": user_data.role,
            "activeBid": activeBids,
            # "activeBidss": activeBidss,
            "activeBidss": bidList,
            "purchasedInvoices": page_obj,
            "purchasedInvoicesCount": purchasedInvoicesCount,
            "completedInvoices":completedInvoices,
            "totalPurchases":totalPurchases,
            "invoices":invoices,
            "noOfInvoices":noOfInvoices,
        }
        if user_data.role == "investor":
            return render(request,"investor/bids.html", return_data)
        else:
            return_data = {
                "success": False,
                "message": "You are not authorized to access this page!",
                "status" : 205,
            }
            return render(request,"onboarding/login.html", return_data) 
    except jwt.exceptions.ExpiredSignatureError:
        return_data = {
            "error": "1",
            "message": "Token has expired"
            }
        return render(request,"onboarding/login.html", return_data)


@api_view(["GET"])
def stats_page(request):
    # if 'token' in request.session:
    try:
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        completedInvoices = Invoice.objects.filter(seller_id=user_id, invoice_state=4).count()
        totalSold = Invoice.objects.filter(seller_id=user_id, invoice_state=4).aggregate(Sum('invoice_amount'))
        vendors = Invoice.objects.filter(seller_id=user_id).values('vendor_name').distinct().count()
        recent_activities = RecentActivity.objects.filter(user_id=user_id).order_by('-date_added')[:3]

        completedInvoices = Invoice.objects.filter(seller_id=user_id, invoice_state=4).count()
        totalSold = Invoice.objects.filter(seller_id=user_id, invoice_state=3).aggregate(Sum('invoice_amount'))
        vendors = Invoice.objects.filter(seller_id=user_id).values('vendor_name').distinct().count()
        return_data = {
            "success": True,
            "status" : 200,
            "activated": user_data.verified,
            "message": "Successfull",
            "token": request.session['token'],
            "user_id": user_data.user_id,
            "name": user_data.name,
            "avatar": 'http://'+get_current_site(request).domain+'/media/'+str(user_data.avatar_url),
            "company_name": user_data.company_name,
            "role": user_data.role,
             "vendors":vendors,
            "totalSold":totalSold,
            "completed": completedInvoices,
            "recent_activities": recent_activities,
            "vendors":vendors,
            "totalSold":totalSold,
            "completed": completedInvoices,
        }
        if user_data.role == "seller":
            return render(request,"seller/stats.html", return_data)
        elif user_data.role == "investor":
            return render(request,"investor/stats.html", return_data)
        elif user_data.role == "vendor":
            return render(request,"seller/stats.html", return_data)
        else:
            return_data = {
                "success": False,
                "message": "You are not authorized to access this page!",
                "status" : 205,
            }
            return render(request,"onboarding/login.html", return_data) 
    except jwt.exceptions.ExpiredSignatureError:
        return_data = {
            "error": "1",
            "message": "Token has expired"
            }
        return render(request,"onboarding/login.html", return_data)

# SELLER SIGN UP API
@api_view(["POST"])
def seller_signup(request):
    try:
        role= "seller"
        email = request.data.get('s_email',None)
        userRandomId = "QS-"+string_generator.memo(32) # generate user_id or memo
        business_type = request.data.get('s_business_type',None)
        company_name = request.data.get('s_company',None)
        password = request.data.get('s_password',None)
        company_address = request.data.get('s_address',None)
        cac_no = request.data.get('s_cac',None)

        if User.objects.filter(email=email).exists():
            return_data = {
                "success": False,
                "header": "Email Already Exist!",
                "status" : 201,
                "message": "Sorry! this "+str(email)+" account Exists in our database. Kindly log in or reset your password."
            }
        elif validator.checkmail(email) == False:
            return_data = {
                "success": False,
                "header": "Invalid Email",
                "status" : 201,
                "message": "This email "+str(email)+" entered is Invalid"
            }
        else:
            #encrypt password
            encryped_password = password_functions.generate_password_hash(password)
            #Save user_data
            latestScore = credit_score.creditScoreNew(float(0.01))
            newUserData = User(user_id=userRandomId,business_type=business_type,company_name=company_name,
                                email=email, password=encryped_password,company_address=company_address, role=role, credit_score=latestScore)
            newUserData.save()
            
            balance = Wallet(user=newUserData, token_balance=0, fiat_equivalent=0)
            balance.save()
            
            # save user verification datat
            InitialVerificationData = Verification(user=newUserData,cac_no=cac_no)
            InitialVerificationData.save()
            # Get User Account Verification item
            validated = User.objects.get(user_id=userRandomId).email_verified

            #Generate token
            timeLimit= datetime.datetime.utcnow() + datetime.timedelta(minutes=1440) #set duration for token
            payload = {"user_id": f"{userRandomId}",
                        "validated": validated,
                        "exp":timeLimit}
            token = jwt.encode(payload,settings.SECRET_KEY)
            
            # Send mail using SMTP
            current_site = get_current_site(request)
            mail_subject = 'Activate your Quidroo account.'
            email = {
                'subject': mail_subject,
                'html': '<section style="background-color: #EEF1F8;height:auto;width: auto;display: flex;flex-direction: column;align-items: center;justify-content: center;"> <div style="background: #FFFFFF;width: 100%;padding: 10vh;"><img src="https://i.im.ge/2021/09/23/TCyJRy.jpg" style="margin:auto; width:40%; height: auto;" /><h3 style="margin-top:-6vh;">Hello '+str(company_name)+'!</h3><p style="font-size: 1.15rem;color:#767E9F;">kindly click on the button below to activate your Quidroo Account</p> <a style="background-color: #5151E0;color: #fff; padding: 15px 25px;border: 0;font-size: 1rem;font-weight: 100;border-radius: 5px; text-decoration:none;" href="http://'+current_site.domain+'/verify/'+token+'">Click Here</a></p></div></section>',
                'text': 'Hello, '+str(company_name)+'!\nKindly click on the button below to activate your Quidroo Account',
                'from': {'name': 'Quidroo', 'email': sender_email},
                'to': [
                    {'name': company_name, 'email': email}
                ]
            }
            sentMail = SPApiProxy.smtp_send_mail(email)
            if newUserData and sentMail and InitialVerificationData:
                newActivity = RecentActivity(activity="Signed up as a Seller", user_id=newUserData.user_id)
                newActivity.save()
                return_data = {
                    "success": True,
                    "status" : 200,
                    "header": "Confirm Your Email",
                    "message": "Hello! Thank you for registering on Quidroo. We’ve sent a message to "+str(newUserData.email)+" with a link to activate your account. To complete your registration, please check and confirm your email address.",
                    "user_id": userRandomId,
                    "token": token,
                    "elapsed_time": f"{timeLimit}",
                    }
    except Exception as e:
        return_data = {
            "success": False,
            "header": "Server Error!",
            "status" : 202,
            "message": str(e)
        }
    return render(request,"onboarding/email_confirmation.html", return_data)

# INVESTOR COMPANY SIGN UP API
@api_view(["POST"])
def investor_company_signup(request):
    try:
        role= "investor"
        email = request.data.get('ic_email',None)
        userRandomId = "QIC-"+string_generator.memo(32) # generate user_id or memo
        business_type = request.data.get('ic_business_type',None)
        company_name = request.data.get('ic_company',None)
        password = request.data.get('ic_password',None)
        company_address = request.data.get('ic_address',None)
        cac_no = request.data.get('ic_cac',None)

        if User.objects.filter(email=email).exists():
            return_data = {
                "success": False,
                "header": "Email Already Exist!",
                "status" : 201,
                "message": "Sorry! this "+str(email)+" account Exists in our database. Kindly log in or reset your password."
            }
        elif validator.checkmail(email) == False:
            return_data = {
                "success": False,
                "header": "Invalid Email",
                "status" : 201,
                "message": "This email "+str(email)+" entered is Invalid"
            }
        else:
            #encrypt password
            encryped_password = password_functions.generate_password_hash(password)
            #Save user_data
            newUserData = User(user_id=userRandomId,business_type=business_type,company_name=company_name,
                                email=email, password=encryped_password,company_address=company_address, role=role)
            newUserData.save()
            # save user verification datat
            InitialVerificationData = Verification(user=newUserData,cac_no=cac_no)
            InitialVerificationData.save()

            balance = Wallet(user=newUserData, token_balance=0, fiat_equivalent=0)
            balance.save()

            # Get User Account Verification item
            validated = User.objects.get(user_id=userRandomId).email_verified

            #Generate token
            timeLimit= datetime.datetime.utcnow() + datetime.timedelta(minutes=1440) #set duration for token
            payload = {"user_id": f"{userRandomId}",
                        "validated": validated,
                        "exp":timeLimit}
            token = jwt.encode(payload,settings.SECRET_KEY)
            
            # Send mail using SMTP
            current_site = get_current_site(request)
            mail_subject = 'Activate your Quidroo account.'
            email = {
                'subject': mail_subject,
                'html': '<section style="background-color: #EEF1F8;height:auto;width: auto;display: flex;flex-direction: column;align-items: center;justify-content: center;"> <div style="background: #FFFFFF;width: 100%;padding: 10vh;"><img src="https://i.im.ge/2021/09/23/TCyJRy.jpg" style="margin:auto; width:40%; height: auto;" /><h3 style="margin-top:-6vh;">Hello '+str(company_name)+'!</h3><p style="font-size: 1.15rem;color:#767E9F;">kindly click on the button below to activate your Quidroo Account</p> <a style="background-color: #5151E0;color: #fff; padding: 15px 25px;border: 0;font-size: 1rem;font-weight: 100;border-radius: 5px; text-decoration:none;" href="http://'+current_site.domain+'/verify/'+token+'">Click Here</a></p></div></section>',
                'text': 'Hello, '+str(company_name)+'!\nKindly click on the button below to activate your Quidroo Account',
                'from': {'name': 'Quidroo', 'email': sender_email},
                'to': [
                    {'name': company_name, 'email': email}
                ]
            }
            sentMail = SPApiProxy.smtp_send_mail(email)
            if newUserData and sentMail and InitialVerificationData:
                newActivity = RecentActivity(activity="Signed up as a Investor", user_id=newUserData.user_id)
                newActivity.save()
                return_data = {
                    "success": True,
                    "status" : 200,
                    "header": "Confirm Your Email",
                    "message": "Hello! Thank you for registering on Quidroo. We’ve sent a message to "+str(newUserData.email)+" with a link to activate your account. To complete your registration, please check and confirm your email address.",
                    "user_id": userRandomId,
                    "token": token,
                    "elapsed_time": f"{timeLimit}",
                    }
    except Exception as e:
        return_data = {
            "success": False,
            "header": "Server Error!",
            "status" : 202,
            "message": str(e)
        }
    return render(request,"onboarding/email_confirmation.html", return_data)

# INVESTOR INDIVIDUAL SIGN UP API
@api_view(["POST"])
def investor_individual_signup(request):
    try:
        role= "investor"
        email = request.data.get('ii_email',None)
        userRandomId = "QII-"+string_generator.memo(32) # generate user_id or memo
        name = request.data.get('ii_name',None)
        phone = request.data.get('ii_phone',None)
        password = request.data.get('ii_password',None)
        address = request.data.get('ii_address',None)
        if User.objects.filter(email=email).exists():
            return_data = {
                "success": False,
                "header": "Email Already Exist!",
                "status" : 201,
                "message": "Sorry! this "+str(email)+" account Exists in our database. Kindly log in or reset your password."
            }
        elif validator.checkmail(email) == False:
            return_data = {
                "success": False,
                "header": "Invalid Email",
                "status" : 201,
                "message": "This email "+str(email)+" entered is Invalid"
            }
        else:
            #encrypt password
            encryped_password = password_functions.generate_password_hash(password)
            #Save user_data
            newUserData = User(user_id=userRandomId,phone=phone,name=name,
                                email=email, password=encryped_password,company_address=address, role=role)
            newUserData.save()
            # save user verification datat
            InitialVerificationData = Verification(user=newUserData)
            InitialVerificationData.save()
            # Get User Account Verification item
            validated = User.objects.get(user_id=userRandomId).email_verified

            balance = Wallet(user=newUserData, token_balance=0, fiat_equivalent=0)
            balance.save()


            #Generate token
            timeLimit= datetime.datetime.utcnow() + datetime.timedelta(minutes=1440) #set duration for token
            payload = {"user_id": f"{userRandomId}",
                        "validated": validated,
                        "exp":timeLimit}
            token = jwt.encode(payload,settings.SECRET_KEY)
            
            # Send mail using SMTP
            current_site = get_current_site(request)
            mail_subject = 'Activate your Quidroo account.'
            email = {
                'subject': mail_subject,
                'html': '<section style="background-color: #EEF1F8;height:auto;width: auto;display: flex;flex-direction: column;align-items: center;justify-content: center;"> <div style="background: #FFFFFF;width: 100%;padding: 10vh;"><img src="https://i.im.ge/2021/09/23/TCyJRy.jpg" style="margin:auto; width:40%; height: auto;" /><h3 style="margin-top:-6vh;">Hello '+str(name)+'!</h3><p style="font-size: 1.15rem;color:#767E9F;">kindly click on the button below to activate your Quidroo Account</p> <a style="background-color: #5151E0;color: #fff; padding: 15px 25px;border: 0;font-size: 1rem;font-weight: 100;border-radius: 5px; text-decoration:none;" href="http://'+current_site.domain+'/verify/'+token+'">Click Here</a></p></div></section>',
                'text': 'Hello, '+str(name)+'!\nKindly click on the button below to activate your Quidroo Account',
                'from': {'name': 'Quidroo', 'email': sender_email},
                'to': [
                    {'name': name, 'email': email}
                ]
            }
            sentMail = SPApiProxy.smtp_send_mail(email)
            if newUserData and sentMail:
                newActivity = RecentActivity(activity="Signed up as a Investor", user_id=newUserData.user_id)
                newActivity.save()
                return_data = {
                    "success": True,
                    "status" : 200,
                    "header": "Confirm Your Email",
                    "message": "Hello! Thank you for registering on Quidroo. We’ve sent a message to "+str(newUserData.email)+" with a link to activate your account. To complete your registration, please check and confirm your email address.",
                    "user_id": userRandomId,
                    "token": token,
                    "elapsed_time": f"{timeLimit}",
                    }
    except Exception as e:
        return_data = {
            "success": False,
            "header": "Server Error!",
            "status" : 202,
            "message": str(e)
        }
    return render(request,"onboarding/email_confirmation.html", return_data)

# VENDOR SIGN UP API
@api_view(["POST"])
def vendor_signup(request):
    try:
        role= "vendor"
        email = request.data.get('v_email',None)
        userRandomId = "QV-"+string_generator.memo(32) # generate user_id or memo
        business_type = request.data.get('v_business_type',None)
        company_name = request.data.get('v_company',None)
        password = request.data.get('v_password',None)
        company_address = request.data.get('v_address',None)
        cac_no = request.data.get('v_cac',None)

        if User.objects.filter(email=email).exists():
            return_data = {
                "success": False,
                "header": "Email Already Exist!",
                "status" : 201,
                "message": "Sorry! this "+str(email)+" account Exists in our database. Kindly log in or reset your password."
            }
        elif validator.checkmail(email) == False:
            return_data = {
                "success": False,
                "header": "Invalid Email",
                "status" : 201,
                "message": "This email "+str(email)+" entered is Invalid"
            }
        else:
            #encrypt password
            encryped_password = password_functions.generate_password_hash(password)
            #Save user_data
            newUserData = User(user_id=userRandomId,business_type=business_type,company_name=company_name,
                                email=email, password=encryped_password,company_address=company_address, role=role)
            newUserData.save()
            # save user verification datat
            InitialVerificationData = Verification(user=newUserData,cac_no=cac_no)
            InitialVerificationData.save()

            balance = Wallet(user=newUserData, token_balance=0, fiat_equivalent=0)
            balance.save()


            # Get User Account Verification item
            validated = User.objects.get(user_id=userRandomId).email_verified

            #Generate token
            timeLimit= datetime.datetime.utcnow() + datetime.timedelta(minutes=1440) #set duration for token
            payload = {"user_id": f"{userRandomId}",
                        "validated": validated,
                        "exp":timeLimit}
            token = jwt.encode(payload,settings.SECRET_KEY)
            
            # Send mail using SMTP
            current_site = get_current_site(request)
            mail_subject = 'Activate your Quidroo account.'
            email = {
                'subject': mail_subject,
                'html': '<section style="background-color: #EEF1F8;height:auto;width: auto;display: flex;flex-direction: column;align-items: center;justify-content: center;"> <div style="background: #FFFFFF;width: 100%;padding: 10vh;"><img src="https://i.im.ge/2021/09/23/TCyJRy.jpg" style="margin:auto; width:40%; height: auto;" /><h3 style="margin-top:-6vh;">Hello '+str(company_name)+'!</h3><p style="font-size: 1.15rem;color:#767E9F;">kindly click on the button below to activate your Quidroo Account</p> <a style="background-color: #5151E0;color: #fff; padding: 15px 25px;border: 0;font-size: 1rem;font-weight: 100;border-radius: 5px; text-decoration:none;" href="http://'+current_site.domain+'/verify/'+token+'">Click Here</a></p></div></section>',
                'text': 'Hello, '+str(company_name)+'!\nKindly click on the button below to activate your Quidroo Account',
                'from': {'name': 'Quidroo', 'email': sender_email},
                'to': [
                    {'name': company_name, 'email': email}
                ]
            }
            sentMail = SPApiProxy.smtp_send_mail(email)
            if newUserData and sentMail and InitialVerificationData:
                newActivity = RecentActivity(activity="Signed up as a Vendor", user_id=newUserData.user_id)
                newActivity.save()
                return_data = {
                    "success": True,
                    "status" : 200,
                    "header": "Confirm Your Email",
                    "message": "Hello! Thank you for registering on Quidroo. We’ve sent a message to "+str(newUserData.email)+" with a link to activate your account. To complete your registration, please check and confirm your email address.",
                    "user_id": userRandomId,
                    "token": token,
                    "elapsed_time": f"{timeLimit}",
                    }
    except Exception as e:
        return_data = {
            "success": False,
            "header": "Server Error!",
            "status" : 202,
            "message": str(e)
        }
    return render(request,"onboarding/email_confirmation.html", return_data)

@api_view(["GET"])
def verify_email(request, token):
    decrypedToken = jwt.decode(token,settings.SECRET_KEY, algorithms=['HS256'])
    try:
        user_id = decrypedToken['user_id']
        if user_id != None and user_id != '':
            #get user info
            user_data = User.objects.get(user_id=user_id)
            if user_data :
                user_data.email_verified = True  #change email verfication status
                user_data.save()
                return_data = {
                    "success": True,
                    "status" : 200,
                    "role" : user_data.role,
                    "message": str(user_data.company_name) or str(user_data.name)+", your Quidroo Account is now Verified! Kindly go back to log in"
                }
                return render(request,"onboarding/email_login.html", return_data)
        else:
            return_data = {
                "success": False,
                "status" : 201,
                "header": "Ooops!",
                "message": "This account does not exist!"
            }
    except Exception as e:
        return_data = {
            "success": False,
            "status" : 202,
            "header": "Server Error!",
            "message": str(e)
        }
    return render(request,"onboarding/email_confirmation.html", return_data)

#SIGNIN API
@api_view(["POST"])
def signin(request):
    
    try:
        email = request.data.get("el_email",None) or request.data.get("rl_email",None) or request.data.get("l_email",None)
        password = request.data.get("el_password",None) or request.data.get("rl_password",None) or request.data.get("l_password",None) 
        validate_mail = validator.checkmail(email)
        if validate_mail == True:
            if User.objects.filter(email =email).exists() == False:
                return_data = {
                    "success": False,
                    "status" : 202,
                    "message": "User does not exist"
                }
            else:
                user_data = User.objects.get(email=email)
                is_valid_password = password_functions.check_password_match(password,user_data.password)
                is_verified = user_data.email_verified
                is_activated = user_data.verified
                #Generate token
                timeLimit= datetime.datetime.utcnow() + datetime.timedelta(minutes=1440) #set limit for user
                payload = {"user_id": f'{user_data.user_id}',
                            "validated": is_verified,
                            "exp":timeLimit}
                token = jwt.encode(payload,settings.SECRET_KEY)
                # save token
                request.session['token'] = token
                request.session['credit_score'] = user_data.credit_score

                if is_valid_password and is_verified:
                    newActivity = RecentActivity(activity="Just Logged in", user_id=user_data.user_id)
                    newActivity.save()
                    return_data = {
                        "success": True,
                        "status" : 200,
                        "activated": is_activated,
                        "message": "Successfull",
                        "token": token,
                        "company_name": user_data.company_name,
                        "token-expiration": f"{timeLimit}",
                        "sessionToken":request.session['token'],
                        "creditScore":user_data.credit_score,
                        "user_id": user_data.user_id,
                        "role": f"{user_data.role}",
                    }
                    if user_data.role == "seller":
                        return redirect('/dashboard')
                    elif user_data.role == "investor":
                        return redirect('/dashboard')
                    elif user_data.role == "vendor":
                        return redirect('/dashboard')
                    else:
                        return_data = {
                            "success": False,
                            "message": "You are not authorized to access this page!",
                            "status" : 205,
                        }
                        return render(request,"onboarding/login.html", return_data)
                elif is_verified == False:
                    return_data = {
                        "success": False,
                        "user_id": user_data.user_id,
                        "message": "This Email is yet to be verified. Kindly check your email for Email Verification Link",
                        "status" : 205,
                        "token": token
                    }
                    return render(request,"onboarding/index.html", return_data)
                else:
                    return_data = {
                        "success": False,
                        "status" : 201,
                        "message" : "Wrong Password"
                    }
        else:
            return_data = {
                "success": False,
                "status" : 201,
                "message": "Email is Invalid"
            }
    except Exception as e:
        return_data = {
            "success": False,
            "status" : 202,
            "message": str(e)
        }
    return render(request,"onboarding/login.html", return_data)

@api_view(["POST"])
def withdraw(request):
    amount = request.data.get("amount",None) 
    try:
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        wallet_data = Wallet.objects.get(user=user_data)
        
        if amount != "" and wallet_data.fiat_equivalent >= float(amount):
            newBalance = wallet_data.fiat_equivalent - float(amount)
            wallet_data.fiat_equivalent = newBalance
            wallet_data.save()
            newTransaction = Transaction(sender_id=user_id, receiver_id="quidroo", fiat_equivalent=float(amount), token_balance=float(amount),transaction_type = "Debit", transaction_note="Withdrawal from Quidroo Account")
            newTransaction.save()
            if wallet_data and newTransaction:
                # Send mail to user using SMTP
                if user_data.name !="":
                    name = user_data.name
                else:
                    name = user_data.company_name 
                email = user_data.email 
                mail_subject = 'Quidroo: Withdrawal Request Successful.'
                email1 = {
                    'subject': mail_subject,
                    'html': '<section style="background-color: #EEF1F8;height:auto;width: auto;display: flex;flex-direction: column;align-items: center;justify-content: center;"> <div style="background: #FFFFFF;width: 100%;padding: 10vh;"><img src="https://i.im.ge/2021/09/23/TCyJRy.jpg" style="margin:auto; width:40%; height: auto;" /><h3 style="margin-top:-6vh;">Hello '+str(name)+'!</h3><p style="font-size: 1.15rem;color:#767E9F;">Your withdrawal request has been received and the fund would be deposited into your Bank account withn 24 hours</p></div></section>',
                    'text': 'Hello, '+str(name)+'!\nYour withdrawal request has been received and the fund would be deposited into your Bank account withn 24 hours',
                    'from': {'name': 'Quidroo', 'email': sender_email},
                    'to': [
                        {'name': name, 'email': email}
                    ]
                }
                sentMail = SPApiProxy.smtp_send_mail(email1)
                # Send mail to ADMIN using SMTP
                if user_data.name !="":
                    name = user_data.name
                else:
                    name = user_data.company_name 
                email = "todak2000@gmail.com"
                mail_subject = str(name)+' just made a Withdrawal Request'
                email2 = {
                    'subject': mail_subject,
                    'html': '<section style="background-color: #EEF1F8;height:auto;width: auto;display: flex;flex-direction: column;align-items: center;justify-content: center;"> <div style="background: #FFFFFF;width: 100%;padding: 10vh;"><img src="https://i.im.ge/2021/09/23/TCyJRy.jpg" style="margin:auto; width:40%; height: auto;" /><h3 style="margin-top:-6vh;">Hello Admin!</h3><p style="font-size: 1.15rem;color:#767E9F;">'+str(name)+' made a withdrawal request. Kindly attend to it within 24 hours.</p></div></section>',
                    'text': 'Hello, Admin!\n '+str(name)+' made a withdrawal request. Kindly attend to it within 24 hours.',
                    'from': {'name': 'Quidroo', 'email': sender_email},
                    'to': [
                        {'name': name, 'email': email}
                    ]
                }
                sentMail2 = SPApiProxy.smtp_send_mail(email2)
                newActivity = RecentActivity(activity="Initiated a withdrawal of NGN "+str(amount), user_id=user_data.user_id)
                newActivity.save()
                return_data = {
                "success": True,
                "status" : 200,
                "activated": user_data.verified,
                "message": "Your withdrawal request has been received and the fund would be deposited into your Bank account withn 24 hours",
                "company_name": user_data.company_name,
                "role": user_data.role,
                "new_fiat_equivalent":wallet_data.fiat_equivalent,
                }
        else:
            return_data = {
                "success": False,
                "message": "Sorry, you have insufficient funds or entered no amount value!",
                "status" : 205,
            }
    except jwt.exceptions.ExpiredSignatureError:
        return_data = {
            "error": "1",
            "message": "Token has expired"
            }
    return Response(return_data)

# FUND USER ACCOUNT
@api_view(["POST"])
def topup(request):
    
    str_amount = request.data.get("amount",None)
    ref = request.data.get("txref",None)
    # if 'token' in request.session: 
    try:
        if str_amount !="":
            amount = float(str_amount) 
            decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decrypedToken['user_id']
            user_data = User.objects.get(user_id=user_id)

            wallet_data = Wallet.objects.get(user=user_data)
            newBalance = wallet_data.fiat_equivalent + amount
            wallet_data.fiat_equivalent = newBalance
            wallet_data.save()

            newTransaction = Transaction(receiver_id=user_id, sender_id="quidroo", fiat_equivalent=amount, token_balance=amount,transaction_type = "Credit", transaction_note="Topup into Quidroo Account", tx_hash=ref)
            newTransaction.save()
            newActivity = RecentActivity(activity="Initiated and completed a Topup of NGN "+str(amount), user_id=user_data.user_id)
            newActivity.save()
            return_data = {
                "success": True,
                "status" : 200,
                "activated": user_data.verified,
                "message": str(user_data.name) or str(user_data.company_name) + "! your Quidroo wallet has been credited successfully with $"+ str(amount),
                "company_name": user_data.company_name,
                "role": user_data.role,
                "new_fiat_equivalent":wallet_data.fiat_equivalent,
            }
                
        else:
            return_data = {
            "success": False,
            "message": "Sorry! you entered no amount value. Kindly enter a real value",
            "status" : 205,
        }
        
    except jwt.exceptions.ExpiredSignatureError:
        return_data = {
            "error": "1",
            "message": "Token has expired"
            }
    return Response(return_data)

@api_view(["POST"])
def upload_invoice(request):
    # file = request.data.get("file",None)
    file= request.FILES['file']
    invoice_name = request.data.get("invoice_name",None)
    invoice_amount = request.data.get("invoice_amount",None)
    datee = request.data.get("invoice_date",None)
    invoice_date= DT.datetime.strptime(datee, '%Y-%m-%d')
    if request.data.get("vendor_name",None) != "":
        vendor_name = request.data.get("vendor_name",None)
    else:
        vendor_name = request.data.get("vendor_name2",None) # from select tag
    vendor_phone = request.data.get("vendor_phone",None)
    vendor_email = request.data.get("vendor_email",None)
    vendor_contact = request.data.get("vendor_contact",None)
    # invoice_file= cloudinary.uploader.upload(file)
    if file is not "":
        if 'token' in request.session: 
            decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decrypedToken['user_id']
            user_data = User.objects.get(user_id=user_id)
            if request.data.get("vendor_name",None) != "":
                newVendor = VendorList(name=vendor_name)
                newVendor.save()
            receivable_amount = float(invoice_amount)*(1-(float(user_data.credit_score)/100))
            newUpload = Invoice(seller_id=user_id, additional_details= invoice_name,invoice_url=file, due_date=invoice_date, vendor_name=vendor_name, vendor_contact_name=vendor_contact,vendor_email  = vendor_email , vendor_phone=vendor_phone, invoice_amount=invoice_amount, receivable_amount=receivable_amount, seller_ror=user_data.credit_score)
            newUpload.save()
            newActivity = RecentActivity(activity="Uploaded an Invoice - "+str(invoice_name), user_id=user_id)
            newActivity.save()
            if newUpload and newActivity:
                return_data = {
                "success": True,
                "status" : 200,
                "activated": user_data.verified,
                "message": str(user_data.name) or str(user_data.company_name) + "! your Invoice has been successfully uploaded and pending approval",
                "company_name": user_data.company_name,
                "role": user_data.role,
                "avatar": 'http://'+get_current_site(request).domain+'/media/'+str(user_data.avatar_url),
                "invoice_url": 'http://'+get_current_site(request).domain+'/media/'+str(newUpload.invoice_url),
                
            }
            else:
                return_data = {
                "success": False,
                "message": "Sorry! an error occured",
                "status" : 205,
                "avatar": 'http://'+get_current_site(request).domain+'/media/'+str(user_data.avatar_url),
            }
            
            
        else:
            return_data = {
                "success": False,
                "message": "Sorry! your session expired. Kindly login again",
                "status" : 205,
            }
    else:
        return_data = {
            "success": False,
            "message": "Sorry! an error occured! try again",
            "status" : 205,
        }
    return render(request,"seller/upload.html", return_data)

@api_view(["POST"])
def invoice_search(request):
    status = request.data.get("status",None)
    date = int(request.data.get("date",None))
    
    if 'token' in request.session:
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        today = DT.date.today()
        selectedDate = today + DT.timedelta(days=date)
        # print("status: ",status)
        # print("date: ",date)
        if status == "all" and date == 0:
            searchInvoices = Invoice.objects.filter(seller_id=user_id).order_by('-created_at')[:20]
        elif status == "all" and date != 0:
            searchInvoices = Invoice.objects.filter(seller_id=user_id, due_date__gte=today, due_date__lte=selectedDate).order_by('-created_at')[:20]
        elif status != "all" and date == 0:
            searchInvoices = Invoice.objects.filter(seller_id=user_id, invoice_state=status).order_by('-created_at')[:20]
        else:
            searchInvoices = Invoice.objects.filter(seller_id=user_id, invoice_state=status, due_date__gte=today, due_date__lte=selectedDate).order_by('-created_at')[:20]
        num = len(searchInvoices)
        searchInvoicesList = []
        for i in range(0,num):
            due_date = searchInvoices[i].due_date
            additional_details  = searchInvoices[i].additional_details
            invoice_amount  = searchInvoices[i].invoice_amount
            invoice_state = searchInvoices[i].invoice_state
            vendor_name = searchInvoices[i].vendor_name
            invoice_url = searchInvoices[i].invoice_url
            to_json = {
                "invoice_state": invoice_state,
                "additional_details": additional_details,
                "invoice_amount": invoice_amount,
                "vendor_name": vendor_name,
                "invoice_url":'http://'+get_current_site(request).domain+'/media/'+str(invoice_url),
                "due_date": due_date.strftime('%Y-%m-%d')
            }
            searchInvoicesList.append(to_json)
        return_data = {
            "success": True,
            "status" : 200,
            "activated": user_data.verified,
            "message": "Successfull",
            "name": user_data.name,
            "token": request.session['token'],
            "user_id": user_data.user_id,
            "company_name": user_data.company_name,
            "role": user_data.role,
            "invoices": searchInvoicesList
        }
        return Response(return_data)
    else:
        return_data = {
            "success": False,
            "message": "Sorry! your session expired. Kindly login again",
            "status" : 205,
        }
        return render(request,"onboarding/login.html", return_data)

@api_view(["POST"])
def invoice_details(request):
    invoice_id = request.data.get("invoice_id",None)   
    if 'token' in request.session:
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        invoiceSelected = Invoice.objects.get(id=invoice_id)
        
        today = DT.date.today()
        # bidClosingDate = today + DT.timedelta(days=3)
        bidClosingDate = invoiceSelected.updated_at + DT.timedelta(days=3)

        return_data = {
            "success": True,
            "status" : 200,
            "activated": user_data.verified,
            "message": "Successfull",
            "now": datetime.date.today(),
            "invoice_state": invoiceSelected.invoice_state,
            "additional_details": invoiceSelected.additional_details,
            "invoice_amount": invoiceSelected.invoice_amount,
            "receivable_amount": invoiceSelected.receivable_amount,
            "vendor_name": invoiceSelected.vendor_name,
            "due_date": invoiceSelected.due_date.strftime('%Y-%m-%d'),
            # "due_date": invoiceSelected.due_date,
            # "invoiceURL":'http://'+get_current_site(request).domain+'/media/'+str(invoiceSelected.invoice_url),
            "approved_time":bidClosingDate
        }
        return Response(return_data)
    else:
        return_data = {
            "success": False,
            "message": "Sorry! your session expired. Kindly login again",
            "status" : 205,
        }
        return render(request,"onboarding/login.html", return_data)
@api_view(["POST"])
def bid_details(request):
    bid_id = request.data.get("bid_id",None)   
    if 'token' in request.session:
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        bidSelected = Bid.objects.get(id=bid_id)
        invoiceSelected = Invoice.objects.get(id=bidSelected.invoice.id)
        totalBids = Bid.objects.filter(invoice__id=invoiceSelected.id).count()
        topBid = Bid.objects.filter(invoice__id=invoiceSelected.id).aggregate(Min('buyer_ror'))
        # exisitedBid = Bid.objects.filter(invoice__id=invoiceSelected.id, bidder_id=user_id)
        # today = DT.date.today()
        bidClosingDate = bidSelected.invoice.updated_at + DT.timedelta(days=3)
        return_data = {
            "success": True,
            "status" : 200,
            "activated": user_data.verified,
            "message": "Successfull",
            "now": datetime.date.today(),
            "invoice_state": invoiceSelected.invoice_state,
            "additional_details": invoiceSelected.additional_details,
            "invoice_amount": invoiceSelected.invoice_amount,
            "receivable_amount": invoiceSelected.receivable_amount,
            "vendor_name": invoiceSelected.vendor_name,
            "due_date": invoiceSelected.due_date.strftime('%Y-%m-%d'),
            # "invoiceURL": invoiceSelected.invoice_url,
            "myBid": bidSelected.buyer_ror,
            "topBid":topBid["buyer_ror__min"],
            "totalBids":totalBids,
            "approved_time":bidClosingDate
        }
        return Response(return_data)
    else:
        return_data = {
            "success": False,
            "message": "Sorry! your session expired. Kindly login again",
            "status" : 205,
        }
        return render(request,"onboarding/login.html", return_data)

@api_view(["POST"])
def upload_verification_data(request):
    decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
    user_id = decrypedToken['user_id']
    user_data = User.objects.get(user_id=user_id)
    if user_data.role == "seller":
        # idCard = request.data.get("file_id",None)
        # pics = request.data.get("pics_id",None) 
        idCard = request.FILES['file_id']
        pics = request.FILES['pics_id']
        cac_cert = request.FILES['cac_cert']
        bank_statement = request.FILES['bank_statement']
        # cac_cert = request.data.get("cac_cert",None)
        # bank_statement = request.data.get("bank_statement",None)

        tin_no = request.data.get("tin_no",None)
        nin_no = request.data.get("nin_no",None)
        verBank = request.data.get("ver-bank",None)
        verAccNo = request.data.get("ver-acc-no",None)
        verAccName = request.data.get("ver-acc-name",None)
        bvn_no = request.data.get("ver-bvn",None)

        # id_cloud= cloudinary.uploader.upload(idCard)
        # pics_cloud= cloudinary.uploader.upload(pics)
        # cac_cloud= cloudinary.uploader.upload(cac_cert)
        # bank_statement_cloud= cloudinary.uploader.upload(bank_statement)

        if decrypedToken:
            # decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
            # user_id = decrypedToken['user_id']
            # user_data = User.objects.get(user_id=user_id)
            newVerData = Verification.objects.get(user=user_data)
            newVerData.user_Idcard=idCard
            newVerData.bank_statement=bank_statement
            newVerData.cac_certificate=cac_cert
            newVerData.nin=nin_no
            newVerData.bvn=bvn_no
            newVerData.account_name=verAccName
            newVerData.account_no=verAccNo
            newVerData.bank=verBank
            newVerData.tin=tin_no
            newVerData.awaiting_approval=True 
            newVerData.save()
            user_data.avatar_url = pics
            user_data.save()
            newActivity = RecentActivity(activity="Uploaded an Verification Data", user_id=user_id)
            newActivity.save()
            if newVerData and newActivity:
                inPercent = float(user_data.credit_score)/100
                latestScore = credit_score.creditScore(inPercent)
                if latestScore <= 0:
                    user_data.credit_score = 0
                else:
                    user_data.credit_score = latestScore
                user_data.save()
                # Send mail to ADMIN using SMTP
                if user_data.name !="":
                    name = user_data.name
                else:
                    name = user_data.company_name 
                email = "todak2000@gmail.com"
                mail_subject = str(name)+' just uploaded their Details'
                email2 = {
                    'subject': mail_subject,
                    'html': '<section style="background-color: #EEF1F8;height:auto;width: auto;display: flex;flex-direction: column;align-items: center;justify-content: center;"> <div style="background: #FFFFFF;width: 100%;padding: 10vh;"><img src="https://i.im.ge/2021/09/23/TCyJRy.jpg" style="margin:auto; width:40%; height: auto;" /><h3 style="margin-top:-6vh;">Hello Admin!</h3><p style="font-size: 1.15rem;color:#767E9F;">'+str(name)+' has uploaded his verification details. Kindly attend to it within 24 hours and approve or confirm disapproval. Thanks.</p></div></section>',
                    'text': 'Hello, Admin!\n '+str(name)+' has uploaded his verification details. Kindly attend to it within 24 hours and approve or confirm disapproval. Thanks.',
                    'from': {'name': 'Quidroo', 'email': sender_email},
                    'to': [
                        {'name': 'Quidroo Admin', 'email': email}
                    ]
                }
                sentMail2 = SPApiProxy.smtp_send_mail(email2)
                return_data = {
                "success": True,
                "status" : 200,
                "activated": user_data.verified,
                "message": "Verification data Successfully uploaded. Your account would be activated shortly after due evaluation. Thanks",
                "token": request.session['token'],
                "user_id": user_data.user_id,
                "name": user_data.name,
                "company_name": user_data.company_name,
                "credit_score": user_data.credit_score,
                "role": user_data.role,
                "avatar": 'http://'+get_current_site(request).domain+'/media/'+str(user_data.avatar_url),
            }
            else:
                return_data = {
                "success": False,
                "message": "Sorry! an error occured",
                "status" : 205,
                "avatar": 'http://'+get_current_site(request).domain+'/media/'+str(user_data.avatar_url),
            }
                
        else:
            return_data = {
                "success": False,
                "message": "Sorry! an error occured! try again",
                "status" : 205,
            }
        return render(request,"seller/verification.html", return_data)
    else:
        # pics = request.data.get("pics_id",None) 
        pics = request.FILES['pics_id']
        verBank = request.data.get("ver-bank",None)
        verAccNo = request.data.get("ver-acc-no",None)
        verAccName = request.data.get("ver-acc-name",None)
        bvn_no = request.data.get("ver-bvn",None)

        # pics_cloud= cloudinary.uploader.upload(pics)
        newVerData = Verification.objects.get(user=user_data)
        newVerData.bvn=bvn_no
        newVerData.account_name=verAccName
        newVerData.account_no=verAccNo
        newVerData.bank=verBank
        newVerData.awaiting_approval=False 
        newVerData.save()
        user_data.avatar_url = pics
        # user_data.avatar_url = pics_cloud["secure_url"]
        user_data.save()
        newActivity = RecentActivity(activity="Updated your Profile Data", user_id=user_id)
        newActivity.save()
        if newVerData and newActivity:
            latestScore = credit_score.creditScore(float(user_data.credit_score))
            user_data.credit_score = latestScore
            user_data.save()
            return_data = {
            "success": True,
            "status" : 200,
            "activated": user_data.verified,
            "message": "data Successfully uploaded.",
            "token": request.session['token'],
            "user_id": user_data.user_id,
            "name": user_data.name,
            "company_name": user_data.company_name,
            "credit_score": user_data.credit_score,
            "role": user_data.role,
            "avatar": 'http://'+get_current_site(request).domain+'/media/'+str(user_data.avatar_url),
        }
        else:
            return_data = {
            "success": False,
            "message": "Sorry! an error occured",
            "status" : 205,
            "avatar": 'http://'+get_current_site(request).domain+'/media/'+str(user_data.avatar_url),
        }
            

        return render(request,"investor/verification.html", return_data)

# MAKE BID API
@api_view(["POST"])
def makebid(request):
    
    str_amount = request.data.get("amount",None)
    buyer_ror = request.data.get("buyer_ror",None)
    invoice_id = request.data.get("invoice_id",None)
    # if 'token' in request.session: 
    try:
        if str_amount !="":
            amount = float(str_amount) 
            decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decrypedToken['user_id']
            user_data = User.objects.get(user_id=user_id)
            userBalance = Wallet.objects.get(user=user_data).fiat_equivalent
            invoiceSelected = Invoice.objects.get(id=invoice_id)
            exisitedBid = Bid.objects.filter(invoice__id=invoiceSelected.id, bidder_id=user_id)
            if exisitedBid:

            # newBiding = Bid(invoice=invoiceSelected,bidder_id=user_id,amount=amount,buyer_ror=buyer_ror)
            # newBiding.save()
            # newActivity = RecentActivity(activity="You just bidded for Invoice-"+str(invoiceSelected.id), user_id=user_data.user_id)
            # newActivity.save()
                return_data = {
                    "success": True,
                    "status" : 205,
                    "activated": user_data.verified,
                    "message": "Sorry! you already bidded for this Invoice" ,
                    "company_name": user_data.company_name,
                    "name": user_data.name,
                    "role": user_data.role,
                }
            elif amount > userBalance:
                return_data = {
                    "success": True,
                    "status" : 205,
                    "activated": user_data.verified,
                    "message": "Sorry! you have insufficient Balance. Kindly Fund your Wallet." ,
                    "company_name": user_data.company_name,
                    "name": user_data.name,
                    "role": user_data.role,
                }
            else:
                newBiding = Bid(invoice=invoiceSelected,bidder_id=user_id,amount=amount,buyer_ror=buyer_ror)
                newBiding.save()
                newActivity = RecentActivity(activity="You just bidded for Invoice-"+str(invoiceSelected.id), user_id=user_data.user_id)
                newActivity.save()
                return_data = {
                    "success": True,
                    "status" : 200,
                    "activated": user_data.verified,
                    "message": "You’ve successfully made a bid. The successful bid within the next 70 hours automatically purchases the invoice." ,
                    "company_name": user_data.company_name,
                    "name": user_data.name,
                    "role": user_data.role,
                }
                
        else:
            return_data = {
            "success": False,
            "message": "Sorry! you entered no amount value. Kindly enter a real value",
            "status" : 205,
        }
        
    except jwt.exceptions.ExpiredSignatureError:
        return_data = {
            "error": "1",
            "message": "Token has expired"
            }
    return Response(return_data)

# EDIT BID API
@api_view(["POST"])
def editbid(request):
    
    str_amount = request.data.get("e_amount",None)
    buyer_ror = request.data.get("e_buyer_ror",None)
    invoice_id = request.data.get("e_invoice_id",None)
    # if 'token' in request.session: 
    try:
        if str_amount !="":
            amount = float(str_amount) 
            decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decrypedToken['user_id']
            user_data = User.objects.get(user_id=user_id)
            exisitedBid = Bid.objects.get(id=invoice_id)
            exisitedBid.amount=amount
            exisitedBid.buyer_ror=buyer_ror
            exisitedBid.save()
            newActivity = RecentActivity(activity="You just edited your bid for Invoice-"+str(exisitedBid.invoice.id), user_id=user_data.user_id)
            newActivity.save()

            return_data = {
                "success": True,
                "status" : 200,
                "activated": user_data.verified,
                "message": "You’ve successfully edited your bid. The top bid within the next 70 hours automatically purchases the invoice." ,
                "company_name": user_data.company_name,
                "name": user_data.name,
                "role": user_data.role,
            }        
        else:
            return_data = {
            "success": False,
            "message": "Sorry! you entered no amount value. Kindly enter a real value",
            "status" : 205,
        }
        
    except jwt.exceptions.ExpiredSignatureError:
        return_data = {
            "error": "1",
            "message": "Token has expired"
            }
    return Response(return_data)

@api_view(["POST"])
def purchase_invoice_search(request):
    date = int(request.data.get("date",None))
    
    if 'token' in request.session:
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        today = DT.date.today()
        selectedDate = today + DT.timedelta(days=date)
        # purchasedInvoices = Invoice.objects.filter(invoice_state=2).order_by('-created_at')[:10]
        # purchasedInvoices = Invoice.objects.filter(winning_buyer_id=user_id).order_by('-created_at')[:10]
        if date == 0:
            # searchInvoices = Invoice.objects.filter(invoice_state=2).order_by('-created_at')[:10]
            searchInvoices = Invoice.objects.filter(winning_buyer_id=user_id, invoice_state=3).order_by('-created_at')[:10]
            # searchInvoices = Invoice.objects.filter(seller_id=user_id).order_by('-created_at')[:20]
        else:
            # searchInvoices = Invoice.objects.filter(invoice_state=2, due_date__gte=today, due_date__lte=selectedDate).order_by('-created_at')[:10]
            searchInvoices = Invoice.objects.filter(winning_buyer_id=user_id,invoice_state=3, due_date__gte=today, due_date__lte=selectedDate).order_by('-created_at')[:10]
            # searchInvoices = Invoice.objects.filter(seller_id=user_id, invoice_state=status, due_date__gte=today, due_date__lte=selectedDate).order_by('-created_at')[:20]
        num = len(searchInvoices)
        searchInvoicesList = []
        for i in range(0,num):
            due_date = searchInvoices[i].due_date
            additional_details  = searchInvoices[i].additional_details
            receivable_amount  = searchInvoices[i].receivable_amount
            invoice_state = searchInvoices[i].invoice_state
            vendor_name = searchInvoices[i].vendor_name
            invoice_url = searchInvoices[i].invoice_url
            to_json = {
                "invoice_state": invoice_state,
                "additional_details": additional_details,
                "receivable_amount": receivable_amount,
                "vendor_name": vendor_name,
                "invoice_url":invoice_url,
                "due_date": due_date.strftime('%Y-%m-%d')
            }
            searchInvoicesList.append(to_json)
        return_data = {
            "success": True,
            "status" : 200,
            "activated": user_data.verified,
            "message": "Successfull",
            "name": user_data.name,
            "token": request.session['token'],
            "user_id": user_data.user_id,
            "company_name": user_data.company_name,
            "role": user_data.role,
            "invoices": searchInvoicesList
        }
        return Response(return_data)
    else:
        return_data = {
            "success": False,
            "message": "Sorry! your session expired. Kindly login again",
            "status" : 205,
        }
        return render(request,"onboarding/login.html", return_data)

def expired_bid_check():

    bids = Bid.objects.filter(bidClosed=False)
    today = DT.datetime.now()
    for bid in bids:
        
        bidClosingDate = bid.invoice.updated_at + DT.timedelta(days=2)
        closingDate = bidClosingDate.strftime('%Y-%m-%d')
        newTime = today.strftime('%Y-%m-%d')
        # print("BidClosing: ", closingDate)
        # print('today: ', newTime)
        if newTime >= closingDate:
            bid.bidClosed = True
            bid.save()
            updateInvoice = Invoice.objects.get(id=bid.invoice.id)
            if bid and updateInvoice.invoice_state != 3: 
                updateInvoice.invoice_state = 3
                winningBidROR = Bid.objects.filter(invoice=updateInvoice).aggregate(Min('created_at'), Min('buyer_ror'))
                winningBid = Bid.objects.get(buyer_ror=winningBidROR['buyer_ror__min'])
                updateInvoice.winning_buyer_id = winningBid.bidder_id
                updateInvoice.save()
                winnerData = User.objects.get(user_id=updateInvoice.winning_buyer_id)
                sellerData = User.objects.get(user_id=updateInvoice.seller_id)
                if updateInvoice:
                    winnerWallet = Wallet.objects.get(user=winnerData)
                    sellerWallet = Wallet.objects.get(user=sellerData)
                    newBalance = winnerWallet.fiat_equivalent - updateInvoice.receivable_amount
                    sellerBalance = sellerWallet.fiat_equivalent + updateInvoice.receivable_amount
                    winnerWallet.fiat_equivalent = newBalance
                    winnerWallet.save()
                    sellerWallet.fiat_equivalent = sellerBalance
                    sellerWallet.save()
                    newTransactionDebit = Transaction(sender_id=updateInvoice.winning_buyer_id, receiver_id= "quidroo", fiat_equivalent=updateInvoice.receivable_amount, token_balance=updateInvoice.receivable_amount,transaction_type = "Debit", transaction_note="Debit for Invoice-"+str(updateInvoice.id))
                    newTransactionDebit.save()
                    newTransactionCredit = Transaction(sender_id="quidroo", receiver_id= updateInvoice.seller_id, fiat_equivalent=updateInvoice.receivable_amount, token_balance=updateInvoice.receivable_amount,transaction_type = "Credit", transaction_note="Credit Payment for Invoice-"+str(updateInvoice.id))
                    newTransactionCredit.save()

                # send email to winner
                if winnerData.name:
                    name = winnerData.name
                else:
                    name = winnerData.company_name
                
                email = winnerData.email
                mail_subject =str(name)+'! You just won the bid for Invoice-'+ str(winningBid.invoice.id)
                email2 = {
                    'subject': mail_subject,
                    'html': '<section style="background-color: #EEF1F8;height:auto;width: auto;display: flex;flex-direction: column;align-items: center;justify-content: center;"> <div style="background: #FFFFFF;width: 100%;padding: 10vh;"><img src="https://i.im.ge/2021/09/23/TCyJRy.jpg" style="margin:auto; width:40%; height: auto;" /><h3 style="margin-top:-6vh;">Hello, '+str(name)+'</h3><p style="font-size: 1.15rem;color:#767E9F;">Congratulations! you just won the bid for Invoice-'+str(bid.invoice.id)+'. Your Quidroo balance has been deduced accordingly. Thanks.</p></div></section>',
                    'text': 'Hello, '+str(name)+'!\n Congratulations! you just won the bid for Invoice-'+str(bid.invoice.id)+'. Your Quidroo balance has been deducted accordingly. Thanks.',
                    'from': {'name': 'Quidroo', 'email': sender_email},
                    'to': [
                        {'name': 'Quidroo Admin', 'email': email}
                    ]
                }
                sentMail2 = SPApiProxy.smtp_send_mail(email2)

                # send email to seller
                if sellerData.name:
                    name = sellerData.name
                else:
                    name = sellerData.company_name
                
                emailTo = sellerData.email
                mail_subject =str(name)+' Congrats! Invoice-'+ str(winningBid.invoice.id)+' has been bought'
                email3 = {
                    'subject': mail_subject,
                    'html': '<section style="background-color: #EEF1F8;height:auto;width: auto;display: flex;flex-direction: column;align-items: center;justify-content: center;"> <div style="background: #FFFFFF;width: 100%;padding: 10vh;"><img src="https://i.im.ge/2021/09/23/TCyJRy.jpg" style="margin:auto; width:40%; height: auto;" /><h3 style="margin-top:-6vh;">Hello, '+str(name)+'</h3><p style="font-size: 1.15rem;color:#767E9F;">Congratulations! your  Invoice-'+str(winningBid.invoice.id)+' has been sold successfully. Kindly withdraw your earnings from your wallet. Thanks.</p></div></section>',
                    'text': 'Hello, '+str(name)+'!\n Congratulations! your  Invoice-'+str(winningBid.invoice.id)+' has been sold successfully. Kindly withdraw your earnings from your wallet. Thanks.',
                    'from': {'name': 'Quidroo', 'email': sender_email},
                    'to': [
                        {'name': 'Quidroo Admin', 'email': emailTo}
                    ]
                }
                sentMail3 = SPApiProxy.smtp_send_mail(email3)

                print("winning ID:", updateInvoice.winning_buyer_id)
                print("winner:", str(winnerData.name) or str(winnerData.company_name))
                print("bid Amount: ", bid.amount)
        


        # if bidClosingDate > today:
        #     bid.bidClosed = True
        #     bid.save()
            # email = "todak2000@gmail.com"
            # mail_subject ='Invoice-'+ str(bid.invoice.id)+'  bids just closed'
            # email2 = {
            #     'subject': mail_subject,
            #     'html': '<section style="background-color: #EEF1F8;height:auto;width: auto;display: flex;flex-direction: column;align-items: center;justify-content: center;"> <div style="background: #FFFFFF;width: 100%;padding: 10vh;"><img src="https://i.im.ge/2021/09/23/TCyJRy.jpg" style="margin:auto; width:40%; height: auto;" /><h3 style="margin-top:-6vh;">Hello Admin!</h3><p style="font-size: 1.15rem;color:#767E9F;">'+str(bid.invoice.id)+' bids just closed. Thanks.</p></div></section>',
            #     'text': 'Hello, Admin!\n Invoice'+str(bid.invoice.id)+' bids just closed. Thanks.',
            #     'from': {'name': 'Quidroo', 'email': sender_email},
            #     'to': [
            #         {'name': 'Quidroo Admin', 'email': email}
            #     ]
            # }
            # sentMail2 = SPApiProxy.smtp_send_mail(email2)
# @api_view(["POST"])
# def fund(request):
#     # user_phone = request.data.get("phone",None)
#     amount = request.POST["amount"]
#     try: 
#         decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
#         user_id = decrypedToken['user_id']
#         user_data = User.objects.get(user_id=user_id)
#         user_wallet = Wallet.objects.get(user=user_data).fiat_equivalent
#         newBalance = user_wallet.walletBalance + float(amount)
#         user_wallet.walletBalance = newBalance
#         user_wallet.save()

#         newTransaction = Transaction(receiver_id=user_id, sender_id="quidroo", fiat_equivalent=amount, token_balance=amount,transaction_type = "Credit", transaction_note="Topup into Quidroo Account")
#         newTransaction.save()
#         newActivity = RecentActivity(activity="Initiated a Topup of NGN "+str(amount), user_id=user_data.user_id)
#         newActivity.save()

#         newTransaction = Transaction(from_id="Vista", to_id=user_data.user_id, transaction_type="Credit", transaction_message="Top-up - Paystack", amount=float(amount))
#         newTransaction.save()
#         if user_data and newTransaction:
#             # Send mail using SMTP
#             mail_subject = user_data.firstname+'! Vista Top-up Update'
#             email = {
#                 'subject': mail_subject,
#                 'html': '<h4>Hello, '+user_data.firstname+'!</h4><p> You payment of NGN'+amount+ ' to your Vista wallet was successful</p>',
#                 'text': 'Hello, '+user_data.firstname+'!\n You payment of NGN'+amount+ ' to your Vista wallet was successful',
#                 'from': {'name': 'Vista Fix', 'email': 'donotreply@wastecoin.co'},
#                 'to': [
#                     {'name': user_data.firstname, 'email': user_data.email}
#                 ]
#             }
#             SPApiProxy.smtp_send_mail(email)
#             return_data = {
#                 "success": True,
#                 "status" : 200,
#                 "message": "Top-Up Successful"
#             }
#         else:
#             return_data = {
#                 "success": False,
#                 "status" : 201,
#                 "message": "something went wrong!"
#             }
#     except Exception as e:
#         return_data = {
#             "success": False,
#             "status" : 201,
#             "message": str(e)
#         }
#     return Response(return_data)


# ADMIN
@api_view(["GET"])
def admin_dashboard_page(request):
    try:
        awaitingInvoices = Invoice.objects.filter(invoice_state=0).order_by('-created_at')
        num1 = len(awaitingInvoices)
        if num1 >=0:
            awaitingList = []
            for i in range(0,num1):
                id= awaitingInvoices[i].id
                due_date = awaitingInvoices[i].due_date
                additional_details  = awaitingInvoices[i].additional_details
                invoice_amount  = awaitingInvoices[i].invoice_amount
                invoice_state = awaitingInvoices[i].invoice_state
                vendor_name = awaitingInvoices[i].vendor_name
                invoice_url = awaitingInvoices[i].invoice_url
                receivable_amount = awaitingInvoices[i].receivable_amount
                to_json = {
                    "invoice_state": invoice_state,
                    "additional_details": additional_details,
                    "invoice_amount": invoice_amount,
                    "vendor_name": vendor_name,
                    "receivable_amount":receivable_amount,
                    "invoice_url":'http://'+get_current_site(request).domain+'/media/'+str(invoice_url),
                    "due_date": due_date,
                    "id":id
                }
                awaitingList.append(to_json)
        biddableInvoices = Invoice.objects.filter(invoice_state=2).order_by('-created_at')
        num2 = len(biddableInvoices)
        if num2 >=0:
            biddableList = []
            for i in range(0,num2):
                id= biddableInvoices[i].id
                due_date = biddableInvoices[i].due_date
                additional_details  = biddableInvoices[i].additional_details
                invoice_amount  = biddableInvoices[i].invoice_amount
                invoice_state = biddableInvoices[i].invoice_state
                vendor_name = biddableInvoices[i].vendor_name
                invoice_url = biddableInvoices[i].invoice_url
                receivable_amount = biddableInvoices[i].receivable_amount
                winning_buyer_id = biddableInvoices[i].winning_buyer_id
                to_json = {
                    "invoice_state": invoice_state,
                    "additional_details": additional_details,
                    "invoice_amount": invoice_amount,
                    "vendor_name": vendor_name,
                    "receivable_amount":receivable_amount,
                    "invoice_url":'http://'+get_current_site(request).domain+'/media/'+str(invoice_url),
                    "due_date": due_date,
                    "id":id,
                    "winning_buyer_id":winning_buyer_id
                }
                biddableList.append(to_json)
        maturedInvoices = Invoice.objects.filter(invoice_state=3).order_by('-created_at')
        num3 = len(maturedInvoices)
        if num3 >=0:
            maturedList = []
            for i in range(0,num3):
                id= maturedInvoices[i].id
                due_date = maturedInvoices[i].due_date
                additional_details  = maturedInvoices[i].additional_details
                invoice_amount  = maturedInvoices[i].invoice_amount
                invoice_state = maturedInvoices[i].invoice_state
                vendor_name = maturedInvoices[i].vendor_name
                invoice_url = maturedInvoices[i].invoice_url
                receivable_amount = maturedInvoices[i].receivable_amount
                to_json = {
                    "invoice_state": invoice_state,
                    "additional_details": additional_details,
                    "invoice_amount": invoice_amount,
                    "vendor_name": vendor_name,
                    "receivable_amount":receivable_amount,
                    "invoice_url":'http://'+get_current_site(request).domain+'/media/'+str(invoice_url),
                    "due_date": due_date,
                    "id":id
                }
                maturedList.append(to_json)
        completedInvoices = Invoice.objects.filter(invoice_state=4).order_by('-created_at')
        num4 = len(completedInvoices)
        if num4 >=0:
            completedList = []
            for i in range(0,num4):
                id= completedInvoices[i].id
                due_date = completedInvoices[i].due_date
                additional_details  = completedInvoices[i].additional_details
                invoice_amount  = completedInvoices[i].invoice_amount
                invoice_state = completedInvoices[i].invoice_state
                vendor_name = completedInvoices[i].vendor_name
                invoice_url = completedInvoices[i].invoice_url
                receivable_amount = completedInvoices[i].receivable_amount
                to_json = {
                    "invoice_state": invoice_state,
                    "additional_details": additional_details,
                    "invoice_amount": invoice_amount,
                    "vendor_name": vendor_name,
                    "receivable_amount":receivable_amount,
                    "invoice_url":'http://'+get_current_site(request).domain+'/media/'+str(invoice_url),
                    "due_date": due_date,
                    "id":id
                }
                completedList.append(to_json)
        return_data = {
            "success": True,
            "status" : 200,
            "invoices": awaitingList,
            "biddable": biddableList, 
            "matured": maturedList, 
            "completed": completedList,

            "invoicesCount":awaitingInvoices.count(),
            "biddableCount":biddableInvoices.count(),
            "maturedCount":maturedInvoices.count(),
            "completedCount":completedInvoices.count()

        }
        return render(request,"admin/dashboard.html", return_data)
    except Exception as e:
        return_data = {
            "success": False,
            "status" : 201,
            "message": str(e)
        }
    return render(request,"admin/dashboard.html", return_data)

@api_view(["POST"])
def approve_invoice(request):
    invoice_id = request.POST["invoice_id"]
    try:
        updatedInvoice = Invoice.objects.get(id=invoice_id)
        awaitingInvoices = Invoice.objects.filter(invoice_state=0).order_by('-created_at')
        num1 = len(awaitingInvoices)
        if num1 >= 0:
            awaitingList = []
            for i in range(0,num1):
                id= awaitingInvoices[i].id
                due_date = awaitingInvoices[i].due_date
                additional_details  = awaitingInvoices[i].additional_details
                invoice_amount  = awaitingInvoices[i].invoice_amount
                invoice_state = awaitingInvoices[i].invoice_state
                vendor_name = awaitingInvoices[i].vendor_name
                invoice_url = awaitingInvoices[i].invoice_url
                receivable_amount = awaitingInvoices[i].receivable_amount
                to_json = {
                    "invoice_state": invoice_state,
                    "additional_details": additional_details,
                    "invoice_amount": invoice_amount,
                    "vendor_name": vendor_name,
                    "receivable_amount":receivable_amount,
                    "invoice_url":'http://'+get_current_site(request).domain+'/media/'+str(invoice_url),
                    "due_date": due_date,
                    "id":id
                }
                awaitingList.append(to_json)
        biddableInvoices = Invoice.objects.filter(invoice_state=2).order_by('-created_at')
        num2 = len(biddableInvoices)
        if num2 >=0:
            biddableList = []
            for i in range(0,num2):
                id= biddableInvoices[i].id
                due_date = biddableInvoices[i].due_date
                additional_details  = biddableInvoices[i].additional_details
                invoice_amount  = biddableInvoices[i].invoice_amount
                invoice_state = biddableInvoices[i].invoice_state
                vendor_name = biddableInvoices[i].vendor_name
                invoice_url = biddableInvoices[i].invoice_url
                receivable_amount = biddableInvoices[i].receivable_amount
                winning_buyer_id = biddableInvoices[i].winning_buyer_id
                to_json = {
                    "invoice_state": invoice_state,
                    "additional_details": additional_details,
                    "invoice_amount": invoice_amount,
                    "vendor_name": vendor_name,
                    "receivable_amount":receivable_amount,
                    "invoice_url":'http://'+get_current_site(request).domain+'/media/'+str(invoice_url),
                    "due_date": due_date,
                    "id":id,
                    "winning_buyer_id":winning_buyer_id
                }
                biddableList.append(to_json)
        maturedInvoices = Invoice.objects.filter(invoice_state=3).order_by('-created_at')
        num3 = len(maturedInvoices)
        if num3 >=0:
            maturedList = []
            for i in range(0,num3):
                id= maturedInvoices[i].id
                due_date = maturedInvoices[i].due_date
                additional_details  = maturedInvoices[i].additional_details
                invoice_amount  = maturedInvoices[i].invoice_amount
                invoice_state = maturedInvoices[i].invoice_state
                vendor_name = maturedInvoices[i].vendor_name
                invoice_url = maturedInvoices[i].invoice_url
                receivable_amount = maturedInvoices[i].receivable_amount
                to_json = {
                    "invoice_state": invoice_state,
                    "additional_details": additional_details,
                    "invoice_amount": invoice_amount,
                    "vendor_name": vendor_name,
                    "receivable_amount":receivable_amount,
                    "invoice_url":'http://'+get_current_site(request).domain+'/media/'+str(invoice_url),
                    "due_date": due_date,
                    "id":id
                }
                maturedList.append(to_json)
        completedInvoices = Invoice.objects.filter(invoice_state=4).order_by('-created_at')
        num4 = len(completedInvoices)
        if num4 >=0:
            completedList = []
            for i in range(0,num4):
                id= completedInvoices[i].id
                due_date = completedInvoices[i].due_date
                additional_details  = completedInvoices[i].additional_details
                invoice_amount  = completedInvoices[i].invoice_amount
                invoice_state = completedInvoices[i].invoice_state
                vendor_name = completedInvoices[i].vendor_name
                invoice_url = completedInvoices[i].invoice_url
                receivable_amount = completedInvoices[i].receivable_amount
                to_json = {
                    "invoice_state": invoice_state,
                    "additional_details": additional_details,
                    "invoice_amount": invoice_amount,
                    "vendor_name": vendor_name,
                    "receivable_amount":receivable_amount,
                    "invoice_url":'http://'+get_current_site(request).domain+'/media/'+str(invoice_url),
                    "due_date": due_date,
                    "id":id
                }
                completedList.append(to_json)
        if updatedInvoice.invoice_state==2:
            pass
        else:
            updatedInvoice.invoice_state=2
            updatedInvoice.save()
        return_data = {
            "success": True,
            "status" : 200,
            "message":"hi successful",
            "invoices": awaitingList,
            "biddable": biddableList, 
            "matured": maturedList, 
            "completed": completedList,
            "invoicesCount":awaitingInvoices.count(),
            "biddableCount":biddableInvoices.count(),
            "maturedCount":maturedInvoices.count(),
            "completedCount":completedInvoices.count() 
        }
        print(return_data)
        return render(request,"admin/dashboard.html", return_data)
    except Exception as e:
        return_data = {
            "success": False,
            "status" : 201,
            "message": str(e)
        }
    return render(request,"admin/dashboard.html", return_data)

@api_view(["POST"])
def admin_invoice_bids(request):
    invoice_id = request.data.get("invoice_id",None)   
    if invoice_id:
        selectedInvoice = Invoice.objects.get(id=invoice_id)
        bids = Bid.objects.filter(invoice__id=selectedInvoice.id).order_by('-created_at')
        num = len(bids)
        bidList = []
        for i in range(0,num):
            bidder_amount = bids[i].amount
            bidder_name  = User.objects.get(user_id=bids[i].bidder_id).name or User.objects.get(user_id=bids[i].bidder_id).company_name
            bidder_ror  = bids[i].buyer_ror
            bidding_time = bids[i].created_at
            if bids[i].invoice.winning_buyer_id == bids[i].bidder_id:
                winner = True
            else:
                winner = False
            to_json = {
                "bidder_amount": bidder_amount,
                "bidder_name": bidder_name ,
                "bidder_ror": bidder_ror,
                "bidding_time": bidding_time.strftime('%Y-%m-%d'),
                "isWinner": winner
            }
            bidList.append(to_json)
        bidClosingDate = selectedInvoice.updated_at + DT.timedelta(days=3)
        return_data = {
            "success": True,
            "status" : 200,
            "now": datetime.date.today(),
            "invoice_state": selectedInvoice.invoice_state,
            "additional_details": selectedInvoice.additional_details,
            "invoice_amount": selectedInvoice.invoice_amount,
            "receivable_amount": selectedInvoice.receivable_amount,
            "vendor_name": selectedInvoice.vendor_name,
            "due_date": selectedInvoice.due_date.strftime('%Y-%m-%d'),
            # "invoiceURL": selectedInvoice.invoice_url,
            "bids": bidList,
            # "bids": [],
            "approved_time":bidClosingDate
        }
        return Response(return_data)
    else:
        return_data = {
            "success": False,
            "message": "Sorry! your session expired. Kindly login again",
            "status" : 205,
        }
        return render(request,"onboarding/login.html", return_data)

@api_view(["GET"])
def close_bids(request):

    bids = Bid.objects.filter(bidClosed=False).order_by('-created_at')
    today = DT.datetime.now()
    # bidsScanned = Bid.objects.filter(bidClosed=False).count()
    nofBidsClosed = 0
    invoicesUpdated = 0
    for bid in bids:
        
        bidClosingDate = bid.invoice.updated_at + DT.timedelta(days=3)  # change bid closing time to 2 or 3 days when ready for production
        closingDate = bidClosingDate.strftime('%Y-%m-%d')
        newTime = today.strftime('%Y-%m-%d')
        # print("BidClosing: ", closingDate)
        # print('today: ', newTime)
        if newTime >= closingDate:
            bid.bidClosed = True
            bid.save()
            nofBidsClosed = nofBidsClosed+1
            updateInvoice = Invoice.objects.get(id=bid.invoice.id)
            if bid and updateInvoice.invoice_state != 3: 
                updateInvoice.invoice_state = 3
                winningBidROR = Bid.objects.filter(invoice=updateInvoice).aggregate(Min('created_at'), Min('buyer_ror'))
                winningBid = Bid.objects.get(buyer_ror=winningBidROR['buyer_ror__min'])
                updateInvoice.winning_buyer_id = winningBid.bidder_id
                updateInvoice.save()
                winnerData = User.objects.get(user_id=updateInvoice.winning_buyer_id)
                sellerData = User.objects.get(user_id=updateInvoice.seller_id)
                if updateInvoice:
                    invoicesUpdated = invoicesUpdated +1
                    winnerWallet = Wallet.objects.get(user=winnerData)
                    sellerWallet = Wallet.objects.get(user=sellerData)
                    newBalance = winnerWallet.fiat_equivalent - updateInvoice.receivable_amount
                    sellerBalance = sellerWallet.fiat_equivalent + updateInvoice.receivable_amount
                    winnerWallet.fiat_equivalent = newBalance
                    winnerWallet.save()
                    sellerWallet.fiat_equivalent = sellerBalance
                    sellerWallet.save()
                    newTransactionDebit = Transaction(sender_id=updateInvoice.winning_buyer_id, receiver_id= "quidroo", fiat_equivalent=updateInvoice.receivable_amount, token_balance=updateInvoice.receivable_amount,transaction_type = "Debit", transaction_note="Debit for Invoice-"+str(updateInvoice.id))
                    newTransactionDebit.save()
                    newTransactionCredit = Transaction(sender_id="quidroo", receiver_id= updateInvoice.seller_id, fiat_equivalent=updateInvoice.receivable_amount, token_balance=updateInvoice.receivable_amount,transaction_type = "Credit", transaction_note="Credit Payment for Invoice-"+str(updateInvoice.id))
                    newTransactionCredit.save()

                # send email to winner
                if winnerData.name:
                    name = winnerData.name
                else:
                    name = winnerData.company_name
                
                email = winnerData.email
                mail_subject =str(name)+'! You just won the bid for Invoice-'+ str(winningBid.invoice.id)
                email2 = {
                    'subject': mail_subject,
                    'html': '<section style="background-color: #EEF1F8;height:auto;width: auto;display: flex;flex-direction: column;align-items: center;justify-content: center;"> <div style="background: #FFFFFF;width: 100%;padding: 10vh;"><img src="https://i.im.ge/2021/09/23/TCyJRy.jpg" style="margin:auto; width:40%; height: auto;" /><h3 style="margin-top:-6vh;">Hello, '+str(name)+'</h3><p style="font-size: 1.15rem;color:#767E9F;">Congratulations! you just won the bid for Invoice-'+str(bid.invoice.id)+'. Your Quidroo balance has been deduced accordingly. Thanks.</p></div></section>',
                    'text': 'Hello, '+str(name)+'!\n Congratulations! you just won the bid for Invoice-'+str(bid.invoice.id)+'. Your Quidroo balance has been deducted accordingly. Thanks.',
                    'from': {'name': 'Quidroo', 'email': sender_email},
                    'to': [
                        {'name': 'Quidroo Admin', 'email': email}
                    ]
                }
                sentMail2 = SPApiProxy.smtp_send_mail(email2)

                # send email to seller
                if sellerData.name:
                    name = sellerData.name
                else:
                    name = sellerData.company_name
                
                emailTo = sellerData.email
                mail_subject =str(name)+' Congrats! Invoice-'+ str(winningBid.invoice.id)+' has been bought'
                email3 = {
                    'subject': mail_subject,
                    'html': '<section style="background-color: #EEF1F8;height:auto;width: auto;display: flex;flex-direction: column;align-items: center;justify-content: center;"> <div style="background: #FFFFFF;width: 100%;padding: 10vh;"><img src="https://i.im.ge/2021/09/23/TCyJRy.jpg" style="margin:auto; width:40%; height: auto;" /><h3 style="margin-top:-6vh;">Hello, '+str(name)+'</h3><p style="font-size: 1.15rem;color:#767E9F;">Congratulations! your  Invoice-'+str(winningBid.invoice.id)+' has been sold successfully. Kindly withdraw your earnings from your wallet. Thanks.</p></div></section>',
                    'text': 'Hello, '+str(name)+'!\n Congratulations! your  Invoice-'+str(winningBid.invoice.id)+' has been sold successfully. Kindly withdraw your earnings from your wallet. Thanks.',
                    'from': {'name': 'Quidroo', 'email': sender_email},
                    'to': [
                        {'name': 'Quidroo Admin', 'email': emailTo}
                    ]
                }
                sentMail3 = SPApiProxy.smtp_send_mail(email3)
                # print("winning ID:", updateInvoice.winning_buyer_id)
                # print("winner:", str(winnerData.name) or str(winnerData.company_name))
                # print("bid Amount: ", bid.amount)
    return_data = {
        "success": True,
        "status" : 200,
        "message":"Bids check ran successfully",
        "nofBidsClosed":nofBidsClosed,
        "invoicesUpdated":invoicesUpdated,
        "bidScanned": bids.count()
    }
    return Response(return_data)

@api_view(["GET"])
def pay_investors(request):
    today = DT.datetime.now()
    bids = Bid.objects.filter(bidClosed=True, invoice__invoice_state =3).order_by('-created_at')
    nofInvestors = 0
    for bid in bids:
        dueDate = bid.invoice.due_date.strftime('%Y-%m-%d')
        newTime = today.strftime('%Y-%m-%d')
        print(dueDate)
        print(newTime)
        if newTime >= dueDate:
            payeeWallet = Wallet.objects.get(user__user_id=bid.bidder_id)
            payeeWallet.fiat_equivalent = payeeWallet.fiat_equivalent+ bid.amount
            payeeWallet.save()
            updateInvoice = Invoice.objects.get(id=bid.invoice.id)
            updateInvoice.invoice_state = 4
            updateInvoice.save()
            newTransactionCredit = Transaction(sender_id="quidroo", receiver_id= bid.bidder_id, fiat_equivalent=bid.amount, token_balance=bid.amount,transaction_type = "Credit", transaction_note="Credit Payment for Invoice-"+str(bid.invoice.id))
            newTransactionCredit.save()
            if updateInvoice and payeeWallet and newTransactionCredit:
                nofInvestors = nofInvestors+1
                # send email to investor
                if payeeWallet.user.name:
                    name = payeeWallet.user.name
                else:
                    name = payeeWallet.user.company_name
                
                email = payeeWallet.user.email
                mail_subject =str(name)+'! Capital + Interest payment for Invoice-'+ str(bid.invoice.id)
                email2 = {
                    'subject': mail_subject,
                    'html': '<section style="background-color: #EEF1F8;height:auto;width: auto;display: flex;flex-direction: column;align-items: center;justify-content: center;"> <div style="background: #FFFFFF;width: 100%;padding: 10vh;"><img src="https://i.im.ge/2021/09/23/TCyJRy.jpg" style="margin:auto; width:40%; height: auto;" /><h3 style="margin-top:-6vh;">Hello, '+str(name)+'</h3><p style="font-size: 1.15rem;color:#767E9F;">Congratulations! you have just been credited (Capital + Interest) for Invoice-'+str(bid.invoice.id)+'. Your Quidroo balance has been credited accordingly. Thanks.</p></div></section>',
                    'text': 'Hello, '+str(name)+'!\n Congratulations! you have just been credited (Capital + Interest) for Invoice-'+str(bid.invoice.id)+'. Your Quidroo balance has been credited accordingly. Thanks.',
                    'from': {'name': 'Quidroo', 'email': sender_email},
                    'to': [
                        {'name': 'Quidroo Admin', 'email': email}
                    ]
                }
                sentMail2 = SPApiProxy.smtp_send_mail(email2)

                # send email to Admin
                
                emailTo = "todak2000@gmail.com"
                mail_subject = 'Capital + Interest payment made for Invoice-'+ str(bid.invoice.id)
                email3 = {
                    'subject': mail_subject,
                    'html': '<section style="background-color: #EEF1F8;height:auto;width: auto;display: flex;flex-direction: column;align-items: center;justify-content: center;"> <div style="background: #FFFFFF;width: 100%;padding: 10vh;"><img src="https://i.im.ge/2021/09/23/TCyJRy.jpg" style="margin:auto; width:40%; height: auto;" /><h3 style="margin-top:-6vh;">Hello, Admin</h3><p style="font-size: 1.15rem;color:#767E9F;">Final payment for  Invoice-'+str(bid.invoice.id)+' to '+str(name)+' has been made.Thanks.</p></div></section>',
                    'text': 'Hello, Admin !\n Final payment for Invoice-'+str(bid.invoice.id)+' to '+str(name)+' has been made. Thanks.',
                    'from': {'name': 'Quidroo', 'email': sender_email},
                    'to': [
                        {'name': 'Quidroo Admin', 'email': emailTo}
                    ]
                }
                sentMail3 = SPApiProxy.smtp_send_mail(email3)
                # print("winning ID:", updateInvoice.winning_buyer_id)
                # print("winner:", str(winnerData.name) or str(winnerData.company_name))
                # print("bid Amount: ", bid.amount)
    return_data = {
        "success": True,
        "status" : 200,
        "message":"Investment checks ran successfully",
        "nofInvestors":nofInvestors,
    }
    return Response(return_data)

@api_view(["GET"])
def admin_sellers(request):
    try:
        approvedSellers = User.objects.filter(role="seller",verified=True).order_by('-created_at')
        unapprovedSellers = User.objects.filter(role="seller",verified=False).order_by('-created_at')
        # approvedSellersCount = User.objects.filter(role="seller",verified=True).count()
        # unapprovedSellersCount = User.objects.filter(role="seller",verified=False).count()
        sellersCount = User.objects.filter(role="seller").count()
        
        return_data = {
            "success": True,
            "status" : 200,
            "approvedSellers": approvedSellers,
            "unapprovedSellers": unapprovedSellers, 
            "approvedSellersCount": approvedSellers.count(), 
            "unapprovedSellersCount": unapprovedSellers.count(),
            "sellersCount":sellersCount
        }
        return render(request,"admin/sellers.html", return_data)
    except Exception as e:
        return_data = {
            "success": False,
            "status" : 201,
            "message": str(e)
        }
    return render(request,"admin/sellers.html", return_data)

@api_view(["GET"])
def admin_investors(request):
    try:
        investors = Wallet.objects.filter(user__role="investor").order_by('-created_at')
        # investorsCount = User.objects.filter(role="investor").count()
        return_data = {
            "success": True,
            "status" : 200,
            "investors": investors,
            "investorsCount":investors.count(),
        }
        return render(request,"admin/investors.html", return_data)
    except Exception as e:
        return_data = {
            "success": False,
            "status" : 201,
            "message": str(e)
        }
    return render(request,"admin/investors.html", return_data)

@api_view(["POST"])
def verify_seller(request):
    seller_id = request.POST["seller_id"]
    try:
        updatedUser = User.objects.get(user_id=seller_id )
        approvedSellers = User.objects.filter(role="seller",verified=True).order_by('-created_at')
        unapprovedSellers = User.objects.filter(role="seller",verified=False).order_by('-created_at')
        # approvedSellersCount = User.objects.filter(role="seller",verified=True).count()
        # unapprovedSellersCount = User.objects.filter(role="seller",verified=False).count()
        sellersCount = User.objects.filter(role="seller").count()
        if updatedUser.verified==True:
            pass
        else:
            updatedUser.verified=True
            updatedUser.save()
        return_data = {
            "success": True,
            "status" : 200,
            "approvedSellers": approvedSellers,
            "unapprovedSellers": unapprovedSellers, 
            "approvedSellersCount": approvedSellers.count(), 
            "unapprovedSellersCount": unapprovedSellers.count(),
            "sellersCount":sellersCount
        }
        return render(request,"admin/sellers.html", return_data)
    except Exception as e:
        return_data = {
            "success": False,
            "status" : 201,
            "message": str(e)
        }
    return render(request,"admin/sellers.html", return_data)

@api_view(["POST"])
def unverify_seller(request):
    seller_id = request.POST["seller_id2"]
    try:
        updatedUser = User.objects.get(user_id=seller_id )
        approvedSellers = User.objects.filter(role="seller",verified=True).order_by('-created_at')
        unapprovedSellers = User.objects.filter(role="seller",verified=False).order_by('-created_at')
        # approvedSellersCount = User.objects.filter(role="seller",verified=True).count()
        # unapprovedSellersCount = User.objects.filter(role="seller",verified=False).count()
        sellersCount = User.objects.filter(role="seller").count()

        if updatedUser.verified==True:
            updatedUser.verified=False
            updatedUser.save()
            
            return_data = {
                "success": True,
                "status" : 200,
                "message": "successful",
                "approvedSellers": approvedSellers,
                "unapprovedSellers": unapprovedSellers, 
                "approvedSellersCount": approvedSellers.count(), 
                "unapprovedSellersCount": unapprovedSellers.count(),
                "sellersCount":sellersCount
            }
        else:
            pass
        return render(request,"admin/sellers.html", return_data)
    except Exception as e:
        return_data = {
            "success": False,
            "status" : 201,
            "message": str(e)
        }
    return render(request,"admin/sellers.html", return_data)

@api_view(["GET"])
def admin_payment(request):
    try:
        paymentRequests = Transaction.objects.filter(receiver_id="quidroo", paidByQuidroo=False, transaction_note="Withdrawal from Quidroo Account").order_by('-created_at')
        # paymentRequestsCount= Transaction.objects.filter(receiver_id="quidroo", paidByQuidroo=False, transaction_note="Withdrawal from Quidroo Account").count()
        return_data = {
            "success": True,
            "status" : 200,
            "paymentRequests": paymentRequests,
            "paymentRequestsCount":paymentRequests.count()
        }
        return render(request,"admin/payment.html", return_data)
    except Exception as e:
        return_data = {
            "success": False,
            "status" : 201,
            "message": str(e)
        }
    return render(request,"admin/payment.html", return_data)

@api_view(["POST"])
def confirm_payment(request):
    tx_id = request.POST["tx_id"]
    try:
        paymentRequests = Transaction.objects.filter(receiver_id="quidroo", paidByQuidroo=False, transaction_note="Withdrawal from Quidroo Account").order_by('-created_at')
        # paymentRequestsCount= Transaction.objects.filter(receiver_id="quidroo", paidByQuidroo=False, transaction_note="Withdrawal from Quidroo Account").count()
        trax = Transaction.objects.get(id=tx_id)
        # payee = User.objects.get(user_id=trax.sender_id)

        if trax.paidByQuidroo==False:
            trax.paidByQuidroo=True
            trax.save()
            
            return_data = {
                "success": True,
                "status" : 200,
                "message": "successful",
                # "payee": payee.name or payee.company_name,
                # "amount": trax.fiat_equivalent, 
                "paymentRequests": paymentRequests,
                "paymentRequestsCount":paymentRequests.count()
            }
        else:
            pass
        return render(request,"admin/payment.html", return_data)
    except Exception as e:
        return_data = {
            "success": False,
            "status" : 201,
            "message": str(e)
        }
    return render(request,"admin/payment.html", return_data)

def testupload(request):
    data = request.FILES['myfile'] # this is my file
    up = Document(docfile = data)
    up.save()
    if up:
        print("successful")
    # return_data = {
    #         "success": False,
    #         "status" : 201,
    #         "message": str(e)
    #     }

    return render(request,"onboarding/index.html")