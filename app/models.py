from django.db import models

# Create your models here.

class User(models.Model):
    class Meta:
        db_table = "Quidroo_user_table"
    user_id = models.CharField(max_length=500,unique=True)
    firstname = models.CharField(max_length=30,verbose_name="Firstname",blank=True)
    lastname = models.CharField(max_length=30,verbose_name="Lastname",blank=True)
    email = models.EmailField(max_length=90, unique=True,verbose_name="Email")
    phone = models.CharField(max_length=15, unique=True, null=True, verbose_name="Telephone number")
    password = models.TextField(max_length=200,verbose_name="Password")
    company_name = models.TextField(max_length=200,verbose_name="Company Name", null=True)
    credit_score = models.TextField(max_length=200,verbose_name="Quidroo Credit Score", null=True)
    role = models.TextField(max_length=50,verbose_name="User role",default="client")
    verified = models.BooleanField(default=False)
    avatar_url = models.CharField(max_length=30, verbose_name="Profile Pics", null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")

    def __str__(self):
        return f"{self.user_id} - {self.firstname} - {self.lastname} - {self.phone} {self.email} - {self.company_name}- {self.credit_score} - {self.role}- {self.avatar_url}"

class Invoice(models.Model):
    class Meta:
        db_table = "Invoice_table"
    invoice_url = models.CharField(max_length=500,unique=True, verbose_name="Invoice Url")
    due_date = models.DateTimeField(auto_now_add=True, verbose_name="Date Invoice is Due")
    vendor_name = models.CharField(max_length=30,verbose_name="Vendor Name",blank=True)
    vendor_contact_name = models.CharField(max_length=30,verbose_name="Vendor Contact Name",blank=True)
    vendor_email = models.EmailField(max_length=90, unique=True,verbose_name="Vendor Email")
    vendor_phone = models.CharField(max_length=15, unique=True, null=True, verbose_name="Vendor Phone")
    additional_details = models.TextField(max_length=2000,verbose_name="Invoice Additional notes")
    invoice_state = models.CharField(max_length=200,verbose_name="Invoice State", null=True)
    winning_buyer_id = models.CharField(max_length=500,unique=True, verbose_name="Winning Buyer/Investor ID")
    seller_id = models.CharField(max_length=500,unique=True, verbose_name="Seller ID")
    seller_ror = models.FloatField(max_length=4,verbose_name="Seller ROR", default=0.09)
    invoice_amount = models.FloatField(max_length=30, verbose_name="Invoice Amount", null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Modified")
    def __str__(self):
        return f"{self.invoice_url} - {self.due_date} - {self.vendor_name} - {self.vendor_phone} {self.invoice_state} - {self.seller}- {self.winning_buyer} - {self.seller_ror}- {self.invoice_amount} - {self.created_at}"

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
    def __str__(self):
        return f"{self.user} - {self.token_balance} - {self.fiat_equivalent} - {self.created_at} - {self.updated_at}"

class Verification(models.Model):
    class Meta:
        db_table = "User_Verification_data_table"
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_Idcard = models.CharField(max_length=300,verbose_name="ID Card",blank=True)
    cac_no = models.CharField(max_length=300,verbose_name="CAC No",  unique=True,blank=True)
    cac_certificate = models.CharField(max_length=300, verbose_name="CAC Certificate")
    nin = models.CharField(max_length=105, unique=True, null=True, verbose_name="NIN")
    bvn = models.CharField(max_length=200,verbose_name="BVN", unique=True, null=True,)
    bank_statement = models.CharField(max_length=200,verbose_name="Bank Statement", null=True)
    account_name = models.CharField(max_length=200,verbose_name="Account Name", null=True)
    account_no = models.TextField(max_length=50,verbose_name="Account Number")
    bank = models.CharField(max_length=30, verbose_name="Bank", null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Modified")
    def __str__(self):
        return f"{self.user} - {self.user_Idcard} - {self.cac_certificate} - {self.nin} {self.bvn} - {self.account_name}- {self.account_no} - {self.bank}- {self.created_at}"

class Transaction(models.Model):
    class Meta:
        db_table = "Transactions_table"
    sender_id = models.CharField(max_length=500,unique=True, verbose_name="Sender")
    receiver_id = models.CharField(max_length=500,unique=True, verbose_name="Reciever")
    token_balance = models.FloatField(max_length=30,verbose_name="Token Amount Transacted",blank=True)
    fiat_equivalent = models.FloatField(max_length=30,verbose_name="Fiat Equivalent",blank=True)
    transaction_note = models.CharField(max_length=30, verbose_name="Transaction note", null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Modified")
    def __str__(self):
        return f"{self.user} - {self.token_balance} - {self.fiat_equivalent} - {self.created_at} - {self.updated_at}"

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