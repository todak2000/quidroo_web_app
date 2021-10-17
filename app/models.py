from django.db import models

# Create your models here.

class User(models.Model):
    class Meta:
        db_table = "Quidroo_user_table"
    user_id = models.CharField(max_length=500,unique=True)
    name = models.CharField(max_length=30,verbose_name="User Names",blank=True)
    email = models.EmailField(max_length=90, unique=True,verbose_name="Email")
    phone = models.CharField(max_length=15, unique=True, null=True, verbose_name="Telephone number")
    password = models.TextField(max_length=200,verbose_name="Password")
    company_name = models.TextField(max_length=200,verbose_name="Company Name", null=True)
    company_address = models.TextField(max_length=200,verbose_name="Company Address", null=True)
    business_type = models.TextField(max_length=200,verbose_name="Business Type", null=True)
    credit_score = models.TextField(max_length=200,verbose_name="Quidroo Credit Score", default= 0.1,null=True)
    role = models.TextField(max_length=50,verbose_name="User role",default="quidroo")
    verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    avatar_url = models.CharField(max_length=30, verbose_name="Profile Pics", null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
   
    def __str__(self):
        return f"{self.user_id} - {self.name} - {self.phone} {self.email} - {self.company_name}- {self.credit_score} - {self.role}- {self.avatar_url}"

class Invoice(models.Model):
    class Meta:
        db_table = "Invoice_table"
    invoice_url = models.CharField(max_length=500,unique=True, verbose_name="Invoice Url")
    due_date = models.DateField(verbose_name="Date Invoice is Due")
    vendor_name = models.CharField(max_length=30,verbose_name="Vendor Name",blank=True)
    vendor_contact_name = models.CharField(max_length=30,verbose_name="Vendor Contact Name",blank=True)
    vendor_email = models.EmailField(max_length=90, verbose_name="Vendor Email")
    vendor_phone = models.CharField(max_length=15, null=True, verbose_name="Vendor Phone")
    additional_details = models.TextField(max_length=2000,verbose_name="Invoice Additional notes")
    # Invoice State info
    # 0 - Awaiting Confirmation
    # 1 - Confirmed by Vendor/Quidroo
    # 2 - Awaiting Buyer (up for bid)
    # 3 - Awaiting Maturity (sold)
    # 4 - Completed (Buyer paid and quidroo settled)
    invoice_state = models.IntegerField(verbose_name="Invoice State", default=0) 
    winning_buyer_id = models.CharField(max_length=500, verbose_name="Winning Buyer/Investor ID")
    seller_id = models.CharField(max_length=500, verbose_name="Seller ID")
    seller_ror = models.FloatField(max_length=4,verbose_name="Seller ROR", default=0.09)
    invoice_amount = models.FloatField(max_length=30, verbose_name="Invoice Amount", null=True)
    receivable_amount = models.FloatField(max_length=30, verbose_name="Receievable Amount", null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Modified")
    def __str__(self):
        return f"{self.invoice_url} - {self.due_date} - {self.vendor_name} - {self.vendor_phone} {self.invoice_state} - {self.seller_id}- {self.winning_buyer_id} - {self.seller_ror}- {self.invoice_amount} - {self.created_at}"

class Bid(models.Model):
    class Meta:
        db_table = "Bids_table"
    interested_buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(max_length=30,verbose_name="Bid Amount",blank=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    buyer_ror = models.FloatField(max_length=4,verbose_name="Buyer ROR", default=0.09)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Modified")
    def __str__(self):
        return f"{self.invoice} - {self.amount} - {self.interested_buyer} - {self.buyer_ror} - {self.created_at}"

class Wallet(models.Model):
    class Meta:
        db_table = "Wallet_table"
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token_balance = models.FloatField(max_length=30,verbose_name="Quidroo Token Balance",blank=True)
    fiat_equivalent = models.FloatField(max_length=30,verbose_name="Fiat Equivalent",blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Modified")
    
    #Blockchain Account
    # memo = models.CharField(max_length=40, unique=True, verbose_name="memo", blank=True)
    # muxed_acct = models.CharField(max_length=100, unique=True, verbose_name="muxed_acct", blank=True)
    def __str__(self):
        return f"{self.user} - {self.token_balance} - {self.fiat_equivalent} - {self.created_at}"

class Verification(models.Model):
    class Meta:
        db_table = "User_Verification_data_table"
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_Idcard = models.CharField(max_length=300,verbose_name="ID Card",blank=True)
    cac_no = models.CharField(max_length=300,verbose_name="CAC No",  unique=True,blank=True)
    cac_certificate = models.CharField(max_length=300, verbose_name="CAC Certificate")
    nin = models.CharField(max_length=105, unique=True, null=True, verbose_name="NIN")
    tin = models.CharField(max_length=105, unique=True, null=True, verbose_name="TIN")
    bvn = models.CharField(max_length=200,verbose_name="BVN", unique=True, null=True,)
    bank_statement = models.CharField(max_length=200,verbose_name="Bank Statement", null=True)
    account_name = models.CharField(max_length=200,verbose_name="Account Name", null=True)
    account_no = models.TextField(max_length=50,verbose_name="Account Number")
    bank = models.CharField(max_length=30, verbose_name="Bank", null=True)
    # approved = models.BooleanField(default=False)
    awaiting_approval = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Modified")
    def __str__(self):
        return f"{self.user} - {self.user_Idcard} - {self.cac_certificate} - {self.nin} {self.bvn} - {self.account_name}- {self.account_no} - {self.bank}- {self.created_at}"

class Transaction(models.Model):
    class Meta:
        db_table = "Transactions_table"
    sender_id = models.CharField(max_length=500, verbose_name="Sender")
    receiver_id = models.CharField(max_length=500, verbose_name="Reciever")
    token_balance = models.FloatField(max_length=30,verbose_name="Token Amount Transacted",blank=True)
    fiat_equivalent = models.FloatField(max_length=30,verbose_name="Fiat Equivalent",blank=True)
    transaction_type = models.CharField(max_length=500,unique=False, verbose_name="Type of Transaction", default="none")
    transaction_note = models.CharField(max_length=30, verbose_name="Transaction note", null=True)
    tx_hash = models.CharField(max_length=1000, verbose_name="Blockhain Transaction Hash", default="395f2c4c0948911df0461865e9a5fc06ad8c537cfc894224fc748fa4a1b5211f")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Modified")
    def __str__(self):
        return f"{self.sender_id} - {self.receiver_id} - {self.token_balance} - {self.fiat_equivalent} - {self.created_at} - {self.transaction_note} - {self.transaction_type} - {self.tx_hash}"

class OnboardingVerification(models.Model):
    class Meta:
        db_table = "Onboarding Account Verification_table"
    # Verify Users
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.TextField(max_length=20,verbose_name="Verification Code",blank=True)
    isVerified = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True,)

    def __str__(self):
        return f"{self.user} - {self.code} - {self.isVerified}"

class VendorList(models.Model):
    class Meta:
        db_table = "Vendor_table"
    # Vendors
    name = models.CharField(max_length=200,verbose_name="Vendor Name",blank=True)
    credit_score = models.TextField(max_length=20,verbose_name="Vendor Credit score",default= 0.09)
    isVerified = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True,)

    def __str__(self):
        return f"{self.name} - {self.credit_score} - {self.isVerified}"

class RecentActivity(models.Model):
    class Meta:
        db_table = "RecentActivty_table"
    # Recent Activities
    activity = models.CharField(max_length=200,verbose_name="Vendor Name",blank=True)
    user_id = models.TextField(max_length=20,verbose_name="Vendor Credit score",default= 0.09)
    date_added = models.DateTimeField(auto_now_add=True,)

    def __str__(self):
        return f"{self.user_id} - {self.activity} - {self.date_added}"