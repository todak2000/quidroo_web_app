# Generated by Django 2.2.10 on 2021-10-17 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_remove_verification_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='receivable_amount',
            field=models.FloatField(max_length=30, null=True, verbose_name='Receievable Amount'),
        ),
    ]