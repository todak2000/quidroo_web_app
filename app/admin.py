from django.contrib import admin

# Register your models here.
from .models import User,Verification, Invoice, Bid, Wallet, Transaction, OnboardingVerification

admin.site.register(User)
admin.site.register(Verification)
admin.site.register(Invoice)
admin.site.register(Bid)
admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(OnboardingVerification)
