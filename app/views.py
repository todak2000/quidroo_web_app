from django.shortcuts import render, redirect

from django.db.models import Sum, Q
from app.models import (User,Verification, Invoice, Bid, Wallet, Transaction, OnboardingVerification)
from CustomCode import (password_functions, string_generator, validator)

from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.http import JsonResponse

from pysendpulse.pysendpulse import PySendPulse
from decouple import config

# REST_API_ID = config("REST_API_ID")
# REST_API_SECRET = config("REST_API_SECRET")
# TOKEN_STORAGE = config("TOKEN_STORAGE")
# MEMCACHED_HOST = config("MEMCACHED_HOST")
# SPApiProxy = PySendPulse(REST_API_ID, REST_API_SECRET, TOKEN_STORAGE, memcached_host=MEMCACHED_HOST)
# sender_email = "donotreply@wastecoin.co"
# Create your views here.
@api_view(["GET"])
def index(request):
    return render(request,"onboarding/index.html") 
