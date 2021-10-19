import datetime as DT
import datetime
from hashlib import new
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
import jwt
from django.db.models import Sum, Q
from app.models import (RecentActivity, User, VendorList,Verification, Invoice, Bid, Wallet, Transaction, OnboardingVerification)
from CustomCode import (password_functions, string_generator, validator, credit_score)

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
        awaitingInvoices = Invoice.objects.filter(seller_id=user_id, invoice_state=0).count()
        confirmedInvoices = Invoice.objects.filter(seller_id=user_id, invoice_state=1).count()
        buyerInvoices = Invoice.objects.filter(seller_id=user_id, invoice_state=2).count()
        soldInvoices = Invoice.objects.filter(seller_id=user_id, invoice_state=3).count()
        completedInvoices = Invoice.objects.filter(seller_id=user_id, invoice_state=4).count()
        totalSold = Invoice.objects.filter(seller_id=user_id, invoice_state=4).aggregate(Sum('invoice_amount'))
        vendors = Invoice.objects.filter(seller_id=user_id).values('vendor_name').distinct().count()
        recent_activities = RecentActivity.objects.filter(user_id=user_id).order_by('-date_added')[:3]
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
            "name": user_data.name,
            "company_name": user_data.company_name,
            "credit_score": user_data.credit_score,
            "role": user_data.role,
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
        if user_data.role == "seller":
            return render(request,"seller/dashboard.html", return_data)
            # return render(request,"seller/wallet.html", return_data)
        elif user_data.role == "investor":
            return render(request,"investor/dashboard.html", return_data)
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
def verification_page(request):
    try:
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        user_ver = Verification.objects.get(user=user_data)
        # awaitingInvoices = Invoice.objects.filter(seller_id=user_id, invoice_state=0).count()
        # confirmedInvoices = Invoice.objects.filter(seller_id=user_id, invoice_state=1).count()
        # buyerInvoices = Invoice.objects.filter(seller_id=user_id, invoice_state=2).count()
        # soldInvoices = Invoice.objects.filter(seller_id=user_id, invoice_state=3).count()
        # completedInvoices = Invoice.objects.filter(seller_id=user_id, invoice_state=4).count()
        # totalSold = Invoice.objects.filter(seller_id=user_id, invoice_state=4).aggregate(Sum('invoice_amount'))
        # vendors = Invoice.objects.filter(seller_id=user_id).values('vendor_name').distinct().count()
        # recent_activities = RecentActivity.objects.filter(user_id=user_id).order_by('-date_added')[:3]
        # wallet_data = Wallet.objects.get(user=user_data)
        # local_tx = Transaction.objects.filter(Q(sender_id=user_id) | Q(receiver_id=user_id)).order_by('-created_at')[:3]

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
            "awaiting_approval": user_ver.awaiting_approval,
           
        }
        if user_data.role == "seller":
            return render(request,"seller/verification.html", return_data)
            # return render(request,"seller/wallet.html", return_data)
        elif user_data.role == "investor":
            return render(request,"seller/dashboard.html", return_data)
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
            "credit_score": user_data.credit_score,
            "name": user_data.name,
            "fiat_equivalent":wallet_data.fiat_equivalent,
            "local_transaction": local_tx,
            "account_name":user_ver.account_name,
            "account_no": user_ver.account_no,
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
        invoices = Invoice.objects.filter(seller_id=user_id).order_by('-created_at')[:10]
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
            "invoices": invoices
        }
        if user_data.role == "seller":
            return render(request,"seller/invoices.html", return_data)
        elif user_data.role == "investor":
            return render(request,"investor/invoices.html", return_data)
        elif user_data.role == "vendor":
            return render(request,"seller/invoices.html", return_data)
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
        return_data = {
            "success": True,
            "status" : 200,
            "activated": user_data.verified,
            "message": "Successfull",
            "token": request.session['token'],
            "user_id": user_data.user_id,
            "name": user_data.name,
            "company_name": user_data.company_name,
            "role": user_data.role,
             "vendors":vendors,
            "totalSold":totalSold,
            "completed": completedInvoices,
            "recent_activities": recent_activities
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
            latestScore = credit_score.creditScore(float(0.01))
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
                    "message": str(user_data.company_name)+", your Quidroo Account is now Verified! Kindly go back to log in"
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

            newTransaction = Transaction(receiver_id=user_id, sender_id="quidroo", fiat_equivalent=amount, token_balance=amount,transaction_type = "Credit", transaction_note="Topup into Quidroo Account", tx_hash=bc["hash"])
            newTransaction.save()
            newActivity = RecentActivity(activity="Initiated a Topup of NGN "+str(amount), user_id=user_data.user_id)
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
    file = request.data.get("file",None)
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
    invoice_file= cloudinary.uploader.upload(file)
    if invoice_file:
        if 'token' in request.session: 
            decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decrypedToken['user_id']
            user_data = User.objects.get(user_id=user_id)
            if request.data.get("vendor_name",None) != "":
                newVendor = VendorList(name=vendor_name)
                newVendor.save()
            receivable_amount = float(invoice_amount)*(1-(float(user_data.credit_score)/100))
            newUpload = Invoice(seller_id=user_id, additional_details= invoice_name,invoice_url=invoice_file["secure_url"], due_date=invoice_date, vendor_name=vendor_name, vendor_contact_name=vendor_contact,vendor_email  = vendor_email , vendor_phone=vendor_phone, invoice_amount=invoice_amount, receivable_amount=receivable_amount, seller_ror=user_data.credit_score)
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
                "invoice_url": newUpload.invoice_url
            }
            else:
                return_data = {
                "success": False,
                "message": "Sorry! an error occured",
                "status" : 205,
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
        print("status: ",status)
        print("date: ",date)
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

@api_view(["POST"])
def invoice_details(request):
    invoice_id = request.data.get("invoice_id",None)   
    if 'token' in request.session:
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        invoiceSelected = Invoice.objects.get(id=invoice_id)
        
        return_data = {
            "success": True,
            "status" : 200,
            "activated": user_data.verified,
            "message": "Successfull",
            "invoice_state": invoiceSelected.invoice_state,
            "additional_details": invoiceSelected.additional_details,
            "invoice_amount": invoiceSelected.invoice_amount,
            "vendor_name": invoiceSelected.vendor_name,
            "due_date": invoiceSelected.due_date.strftime('%Y-%m-%d'),
            "invoiceURL": invoiceSelected.invoice_url
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
    idCard = request.data.get("file_id",None)
    cac_cert = request.data.get("cac_cert",None)
    bank_statement = request.data.get("bank_statement",None)

    tin_no = request.data.get("tin_no",None)
    nin_no = request.data.get("nin_no",None)
    verBank = request.data.get("ver-bank",None)
    verAccNo = request.data.get("ver-acc-no",None)
    verAccName = request.data.get("ver-acc-name",None)
    bvn_no = request.data.get("ver-bvn",None)

    id_cloud= cloudinary.uploader.upload(idCard)
    cac_cloud= cloudinary.uploader.upload(cac_cert)
    bank_statement_cloud= cloudinary.uploader.upload(bank_statement)
    # tin_cloud= cloudinary.uploader.upload(tin_no)
    # nin_cloud= cloudinary.uploader.upload(nin_no)

    # verBank_cloud= cloudinary.uploader.upload(verBank)
    # verAccNo_cloud= cloudinary.uploader.upload(verAccNo)
    # verAccName_cloud= cloudinary.uploader.upload(verAccName)
    # bvn_cloud= cloudinary.uploader.upload(verBvn)
    # if id_cloud:
    if bank_statement_cloud and cac_cloud and id_cloud:
        # if 'token' in request.session: 
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        newVerData = Verification.objects.get(user=user_data)
        newVerData.user_Idcard=id_cloud["secure_url"]
        newVerData.bank_statement=bank_statement_cloud["secure_url"]
        newVerData.cac_certificate=cac_cloud["secure_url"]
        newVerData.nin=nin_no
        newVerData.bvn=bvn_no
        newVerData.account_name=verAccName
        newVerData.account_no=verAccNo
        newVerData.bank=verBank
        newVerData.tin=tin_no
        newVerData.awaiting_approval=True 
        newVerData.save()
        newActivity = RecentActivity(activity="Uploaded an Verification Data", user_id=user_id)
        newActivity.save()
        if newVerData and newActivity:
            latestScore = credit_score.creditScore(float(user_data.credit_score))
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
        }
        else:
            return_data = {
            "success": False,
            "message": "Sorry! an error occured",
            "status" : 205,
        }
            
    else:
        return_data = {
            "success": False,
            "message": "Sorry! an error occured! try again",
            "status" : 205,
        }
    return render(request,"seller/verification.html", return_data)
