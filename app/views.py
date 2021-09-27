import datetime, json
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
import jwt
from django.db.models import Sum, Q
from app.models import (User,Verification, Invoice, Bid, Wallet, Transaction, OnboardingVerification)
from CustomCode import (password_functions, string_generator, validator)

from quidroo import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.http import JsonResponse

from pysendpulse.pysendpulse import PySendPulse
from decouple import config


from blockchain.utils import generate_UID, create_muxed_keypair, get_transaction_history_for_muxed_acct, quidroo_to_user_payments 

REST_API_ID = config("REST_API_ID")
REST_API_SECRET = config("REST_API_SECRET")
TOKEN_STORAGE = config("TOKEN_STORAGE")
MEMCACHED_HOST = config("MEMCACHED_HOST")
SPApiProxy = PySendPulse(REST_API_ID, REST_API_SECRET, TOKEN_STORAGE, memcached_host=MEMCACHED_HOST)
sender_email = "donotreply@wastecoin.co"

#Transaction View for Muxed Account individual users

@api_view(['GET']) #please handle the security
def transaction_history(request):
    '''
    endpoint to return transaction history of a user account
    :params user_muxed_acct:  The muxed account to fetch transaction history
    '''
    user_muxed_acct = request.data
    try:
        acct = user_muxed_acct['user_muxed_acct']
    except:
        return Response({"message":"user_muxed_acct is a required argument"
                        }, status=400)
    else:
        try:
            # Send muxed acct to horizon, this only returns the list of transaction performed by a muxed acct,
            # In case there is no transaction for the muxed acct, it returns an empty list
            tx = get_transaction_history_for_muxed_acct(acct)
        except:
            return Response({
                "message":"Transaction Error"
            }, status=400)
        else:
            return Response({"message":tx}, status=200)




# Create your views here.
@api_view(["GET"])
def index(request): 
    # return render(request,"seller/dashboard.html")
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
def dashboard_page(request):
    if 'token' in request.session:
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        wallet_data = Wallet.objects.get(user=user_data)
        tx = get_transaction_history_for_muxed_acct(wallet_data.muxed_acct)
        return_data = {
            "success": True,
            "status" : 200,
            "activated": user_data.verified,
            "message": "Successfull",
            "token": request.session['token'],
            "user_id": user_data.user_id,
            "company_name": user_data.company_name,
            "role": user_data.role,
            "fiat_equivalent":wallet_data.fiat_equivalent,
            "token_balance":wallet_data.token_balance,
            "muxed_acct": wallet_data.muxed_acct,
            "memo": wallet_data.memo,
            "transactions":tx
        }
        if user_data.role == "seller":
            return render(request,"seller/dashboard.html", return_data)
        elif user_data.role == "investor":
            return render(request,"seller/dashboard.html", return_data)
        elif user_data.role == "vendor":
            return render(request,"seller/dashboard.html", return_data)
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
def wallet_page(request):
    if 'token' in request.session:
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        wallet_data = Wallet.objects.get(user=user_data)
        tx = get_transaction_history_for_muxed_acct(wallet_data.muxed_acct)
        return_data = {
            "success": True,
            "status" : 200,
            "activated": user_data.verified,
            "message": "Successfull",
            "token": request.session['token'],
            "user_id": user_data.user_id,
            "company_name": user_data.company_name,
            "role": user_data.role,
            "fiat_equivalent":wallet_data.fiat_equivalent,
            "token_balance":wallet_data.token_balance,
            "muxed_acct": wallet_data.muxed_acct,
            "memo": wallet_data.memo,
            "transactions":tx
        }
        if user_data.role == "seller":
            return render(request,"seller/wallet.html", return_data)
        elif user_data.role == "investor":
            return render(request,"seller/wallet.html", return_data)
        elif user_data.role == "vendor":
            return render(request,"seller/wallet.html", return_data)
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
def invoices_page(request):
    if 'token' in request.session:
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        return_data = {
            "success": True,
            "status" : 200,
            "activated": user_data.verified,
            "message": "Successfull",
            "token": request.session['token'],
            "user_id": user_data.user_id,
            "company_name": user_data.company_name,
            "role": user_data.role,
        }
        if user_data.role == "seller":
            return render(request,"seller/invoices.html", return_data)
        elif user_data.role == "investor":
            return render(request,"seller/invoices.html", return_data)
        elif user_data.role == "vendor":
            return render(request,"seller/invoices.html", return_data)
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
def stats_page(request):
    if 'token' in request.session:
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        return_data = {
            "success": True,
            "status" : 200,
            "activated": user_data.verified,
            "message": "Successfull",
            "token": request.session['token'],
            "user_id": user_data.user_id,
            "company_name": user_data.company_name,
            "role": user_data.role,
        }
        if user_data.role == "seller":
            return render(request,"seller/stats.html", return_data)
        elif user_data.role == "investor":
            return render(request,"seller/stats.html", return_data)
        elif user_data.role == "vendor":
            return render(request,"seller/stats.html", return_data)
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
        
            newUserData = User(user_id=userRandomId,business_type=business_type,company_name=company_name,
                                email=email, password=encryped_password,company_address=company_address, role=role)
            newUserData.save()
            
            #wallet details updated with muxed and memo saved to db
            user_memo=generate_UID()
            user_muxed_acct =create_muxed_keypair(user_memo)
            balance = Wallet(user=newUserData, token_balance=0, fiat_equivalent=0, memo=user_memo, muxed_acct=user_muxed_acct['muxed_acct'])
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

            #wallet details updated with muxed and memo saved to db
            user_memo=generate_UID()
            user_muxed_acct =create_muxed_keypair(user_memo)
            balance = Wallet(user=newUserData, token_balance=0, fiat_equivalent=0, memo=user_memo, muxed_acct=user_muxed_acct['muxed_acct'])
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

            # Get User Account Verification item
            validated = User.objects.get(user_id=userRandomId).email_verified
            #wallet details updated with muxed and memo saved to db
            user_memo=generate_UID()
            user_muxed_acct =create_muxed_keypair(user_memo)
            balance = Wallet(user=newUserData, token_balance=0, fiat_equivalent=0, memo=user_memo, muxed_acct=user_muxed_acct['muxed_acct'])
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

            #wallet details updated with muxed and memo saved to db
            user_memo=generate_UID()
            user_muxed_acct =create_muxed_keypair(user_memo)
            balance = Wallet(user=newUserData, token_balance=0, fiat_equivalent=0, memo=user_memo, muxed_acct=user_muxed_acct['muxed_acct'])
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

                if is_valid_password and is_verified:
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
    if 'token' in request.session:
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        wallet_data = Wallet.objects.get(user=user_data)
        if wallet_data.fiat_equivalent >= float(amount):
            newBalance = wallet_data.fiat_equivalent - float(amount)
            newBalance.save()
            newTransaction = Transaction(sender_id=user_id, receiver_id="quidroo", fiat_equivalent=float(amount), token_balance=float(amount),transaction_type = "Debit", transaction_note="Withdrawal from Quidroo Account")
            newTransaction.save()
            return_data = {
                "success": True,
                "status" : 200,
                "activated": user_data.verified,
                "message": "Withdrawal Successfull. Within 24 hours. You will be credited into your bank account.",
                "company_name": user_data.company_name,
                "role": user_data.role,
                "new_fiat_equivalent":wallet_data.fiat_equivalent,
                "new_token_balance":wallet_data.token_balance,
            }
            
        else:
            return_data = {
                "success": False,
                "message": "Sorry, you have insufficient funds!",
                "status" : 205,
            }
    else:
        return_data = {
            "success": False,
            "message": "Sorry! your session expired. Kindly login again",
            "status" : 205,
        }
    return Response(return_data)

# FUND USER ACCOUNT
@api_view(["POST"])
def topup(request):
    amount = request.data.get("amount",None) 
    if 'token' in request.session:
        decrypedToken = jwt.decode(request.session['token'],settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decrypedToken['user_id']
        user_data = User.objects.get(user_id=user_id)
        wallet_data = Wallet.objects.get(user=user_data)
        bc = quidroo_to_user_payments(wallet_data.muxed_acct, amount)
        if bc:
            newBalance = wallet_data.fiat_equivalent + float(amount)
            newBalance.save()
            newTransaction = Transaction(receiver_id=user_id, sender_id="quidroo", fiat_equivalent=float(amount), token_balance=float(amount),transaction_type = "Credit", transaction_note="Topup into Quidroo Account")
            newTransaction.save()
            return_data = {
                "success": True,
                "status" : 200,
                "activated": user_data.verified,
                "message": "Fund added Successfull",
                "company_name": user_data.company_name,
                "role": user_data.role,
                "new_fiat_equivalent":wallet_data.fiat_equivalent,
                "new_token_balance":wallet_data.token_balance,
                "blockchain_tx": bc
            }
            
        else:
            return_data = {
                "success": False,
                "message": "Sorry, we could not process the transaction. Kindly try again!",
                "status" : 205,
            }
    else:
        return_data = {
            "success": False,
            "message": "Sorry! your session expired. Kindly login again",
            "status" : 205,
        }
    return Response(return_data)
