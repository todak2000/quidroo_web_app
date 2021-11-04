# Generated by Django 3.2.8 on 2021-10-29 19:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_url', models.CharField(max_length=500, unique=True, verbose_name='Invoice Url')),
                ('due_date', models.DateField(verbose_name='Date Invoice is Due')),
                ('vendor_name', models.CharField(blank=True, max_length=30, verbose_name='Vendor Name')),
                ('vendor_contact_name', models.CharField(blank=True, max_length=30, verbose_name='Vendor Contact Name')),
                ('vendor_email', models.EmailField(max_length=90, verbose_name='Vendor Email')),
                ('vendor_phone', models.CharField(max_length=15, null=True, verbose_name='Vendor Phone')),
                ('additional_details', models.TextField(max_length=2000, verbose_name='Invoice Additional notes')),
                ('invoice_state', models.IntegerField(default=0, verbose_name='Invoice State')),
                ('winning_buyer_id', models.CharField(max_length=500, verbose_name='Winning Buyer/Investor ID')),
                ('seller_id', models.CharField(max_length=500, verbose_name='Seller ID')),
                ('seller_ror', models.FloatField(default=0.09, max_length=4, verbose_name='Seller ROR')),
                ('invoice_amount', models.FloatField(max_length=30, null=True, verbose_name='Invoice Amount')),
                ('receivable_amount', models.FloatField(max_length=30, null=True, verbose_name='Receievable Amount')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('updated_at', models.DateTimeField(auto_now_add=True, verbose_name='Date Modified')),
            ],
            options={
                'db_table': 'Invoice_table',
            },
        ),
        migrations.CreateModel(
            name='RecentActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity', models.CharField(blank=True, max_length=200, verbose_name='Vendor Name')),
                ('user_id', models.TextField(default=0.09, max_length=20, verbose_name='Vendor Credit score')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'RecentActivty_table',
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_id', models.CharField(max_length=500, verbose_name='Sender')),
                ('receiver_id', models.CharField(max_length=500, verbose_name='Reciever')),
                ('token_balance', models.FloatField(blank=True, max_length=30, verbose_name='Token Amount Transacted')),
                ('fiat_equivalent', models.FloatField(blank=True, max_length=30, verbose_name='Fiat Equivalent')),
                ('transaction_type', models.CharField(default='none', max_length=500, verbose_name='Type of Transaction')),
                ('transaction_note', models.CharField(max_length=30, null=True, verbose_name='Transaction note')),
                ('tx_hash', models.CharField(default='395f2c4c0948911df0461865e9a5fc06ad8c537cfc894224fc748fa4a1b5211f', max_length=1000, verbose_name='Blockhain Transaction Hash')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('updated_at', models.DateTimeField(auto_now_add=True, verbose_name='Date Modified')),
            ],
            options={
                'db_table': 'Transactions_table',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=500, unique=True)),
                ('name', models.CharField(blank=True, max_length=30, verbose_name='User Names')),
                ('email', models.EmailField(max_length=90, unique=True, verbose_name='Email')),
                ('phone', models.CharField(max_length=15, null=True, unique=True, verbose_name='Telephone number')),
                ('password', models.TextField(max_length=200, verbose_name='Password')),
                ('company_name', models.TextField(max_length=200, null=True, verbose_name='Company Name')),
                ('company_address', models.TextField(max_length=200, null=True, verbose_name='Company Address')),
                ('business_type', models.TextField(max_length=200, null=True, verbose_name='Business Type')),
                ('credit_score', models.TextField(default=0.1, max_length=200, null=True, verbose_name='Quidroo Credit Score')),
                ('role', models.TextField(default='quidroo', max_length=50, verbose_name='User role')),
                ('verified', models.BooleanField(default=False)),
                ('email_verified', models.BooleanField(default=False)),
                ('avatar_url', models.CharField(max_length=30, null=True, verbose_name='Profile Pics')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
            ],
            options={
                'db_table': 'Quidroo_user_table',
            },
        ),
        migrations.CreateModel(
            name='VendorList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, verbose_name='Vendor Name')),
                ('credit_score', models.TextField(default=0.09, max_length=20, verbose_name='Vendor Credit score')),
                ('isVerified', models.BooleanField(default=False)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'Vendor_table',
            },
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_balance', models.FloatField(blank=True, max_length=30, verbose_name='Quidroo Token Balance')),
                ('fiat_equivalent', models.FloatField(blank=True, max_length=30, verbose_name='Fiat Equivalent')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('updated_at', models.DateTimeField(auto_now_add=True, verbose_name='Date Modified')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.user')),
            ],
            options={
                'db_table': 'Wallet_table',
            },
        ),
        migrations.CreateModel(
            name='Verification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_Idcard', models.CharField(blank=True, max_length=300, verbose_name='ID Card')),
                ('cac_no', models.CharField(blank=True, max_length=300, unique=True, verbose_name='CAC No')),
                ('cac_certificate', models.CharField(max_length=300, verbose_name='CAC Certificate')),
                ('nin', models.CharField(max_length=105, null=True, unique=True, verbose_name='NIN')),
                ('tin', models.CharField(max_length=105, null=True, unique=True, verbose_name='TIN')),
                ('bvn', models.CharField(max_length=200, null=True, unique=True, verbose_name='BVN')),
                ('bank_statement', models.CharField(max_length=200, null=True, verbose_name='Bank Statement')),
                ('account_name', models.CharField(max_length=200, null=True, verbose_name='Account Name')),
                ('account_no', models.TextField(max_length=50, verbose_name='Account Number')),
                ('bank', models.CharField(max_length=30, null=True, verbose_name='Bank')),
                ('awaiting_approval', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('updated_at', models.DateTimeField(auto_now_add=True, verbose_name='Date Modified')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.user')),
            ],
            options={
                'db_table': 'User_Verification_data_table',
            },
        ),
        migrations.CreateModel(
            name='OnboardingVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.TextField(blank=True, max_length=20, verbose_name='Verification Code')),
                ('isVerified', models.BooleanField(default=False)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.user')),
            ],
            options={
                'db_table': 'Onboarding Account Verification_table',
            },
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bidder_id', models.CharField(blank=True, max_length=30, verbose_name='Bidder ID')),
                ('amount', models.FloatField(blank=True, max_length=30, verbose_name='Bid Amount')),
                ('buyer_ror', models.FloatField(default=0.09, max_length=4, verbose_name='Buyer ROR')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('updated_at', models.DateTimeField(auto_now_add=True, verbose_name='Date Modified')),
                ('invoice', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.invoice')),
            ],
            options={
                'db_table': 'Bids_table',
            },
        ),
    ]
