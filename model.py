import random

# Create your models here.
import uuid
from uuid import uuid4

from django.contrib.auth.models import User as usermodel
from django.db import migrations, models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(models.Model): 
    boolChoice = (
        ("M","Male"),("F","Female")
        )
    user = models.ForeignKey(usermodel,on_delete=models.SET_NULL, null=True , blank=True)
    gender = models.CharField(max_length = 1,choices=boolChoice)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Change to DecimalField
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Change to DecimalField
    time_to_give = models.IntegerField()  # Remains as IntegerField
    created_at = models.DateField(auto_now_add=True)
    due_date = models.DateField(auto_created=True)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    permanentad = models.CharField(max_length=20)
    curentad= models.CharField(max_length=20)
    phone = models.CharField(max_length=12)
    citizenshipf = models.ImageField(upload_to='media')
    citizenshipb = models.ImageField(upload_to='media')
    facepic = models.ImageField(upload_to='media')
    bilnumber = models.CharField(max_length=10, blank=True, null=True)  # Allow null and blank
    bondnumber = models.CharField(max_length=10, blank=True, null=True)  # Allow null and blank




    def __str__(self):
        return self.fname


class PaymentDon(models.Model):
    donuser = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment_date = models.DateField(auto_now_add=True)
    user_amount = models.CharField(max_length=10, blank=True, null=True)
    user_fname = models.CharField(max_length=50, blank=True, null=True)  # Store user's first name
    user_lname = models.CharField(max_length=50, blank=True, null=True)  # Store user's last name
    user_email = models.EmailField(max_length=50, blank=True, null=True)  # Store user's email
    user_phone = models.CharField(max_length=15, blank=True, null=True)
    user_permanentad = models.CharField(max_length=20, blank=True, null=True)
    user_curentad= models.CharField(max_length=20, blank=True, null=True)

    user_uuid = models.CharField(max_length=500, blank=True, null=True)  # Ensure this is included
    user_interest = models.CharField(max_length=5, blank=True, null=True)
    user_facepic = models.ImageField(upload_to='media', blank=True, null=True)
    user_citizenshipf = models.ImageField(upload_to='media', blank=True, null=True)
    user_citizenshipb = models.ImageField(upload_to='media', blank=True, null=True)
    user_created_at = models.DateField(max_length=50, blank=True, null=True)
    user_gender = models.CharField(max_length = 50 , blank=True, null=True)
    user_time_to_give = models.CharField(max_length=2,blank=True, null=True)  # Remains as IntegerField
    user_due_date = models.DateField(max_length=50, blank=True, null=True)
    user_bilnumber = models.CharField(max_length=10, blank=True, null=True)
    user_bondnumber = models.CharField(max_length=10, blank=True, null=True)


class Interestpayed(models.Model):

    donusers = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    interest_payment_date = models.DateField(auto_now_add=True)
    interest_amount = models.CharField(max_length=10, blank=True, null=True)
    interest_fname = models.CharField(max_length=50, blank=True, null=True)  # Store user's first name
    interest_lname = models.CharField(max_length=50, blank=True, null=True)  # Store user's last name
    interest_email = models.EmailField(max_length=50, blank=True, null=True)  # Store user's email
    interest_phone = models.CharField(max_length=15, blank=True, null=True)
    interest_permanentad = models.CharField(max_length=20, blank=True, null=True)
    interest_curentad= models.CharField(max_length=20, blank=True, null=True)

    interest_uuid = models.CharField(max_length=500, blank=True, null=True)  # Ensure this is included
    interest_interest = models.CharField(max_length=5, blank=True, null=True)
    interest_facepic = models.ImageField(upload_to='media', blank=True, null=True)
    interest_citizenshipf = models.ImageField(upload_to='media', blank=True, null=True)
    interest_citizenshipb = models.ImageField(upload_to='media', blank=True, null=True)
    interest_created_at = models.DateField(max_length=50, blank=True, null=True)
    interest_gender = models.CharField(max_length = 50 , blank=True, null=True)
    interest_time_to_give = models.CharField(max_length=2,blank=True, null=True)  # Remains as IntegerField
    interest_due_date = models.DateField(max_length=50, blank=True, null=True)
    interest_bilnumber = models.CharField(max_length=10, blank=True, null=True)
    interest_bondnumber = models.CharField(max_length=10, blank=True, null=True)


class Searchmodeldata(models.Model):
    uuid = models.CharField(max_length=200,default=True)
    gender = models.CharField(max_length=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    time_to_give = models.IntegerField()
    created_at = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    permanentad = models.CharField(max_length=20)
    curentad = models.CharField(max_length=20)
    phone = models.CharField(max_length=12)
    citizenshipf = models.ImageField(upload_to='media')
    citizenshipb = models.ImageField(upload_to='media')
    facepic = models.ImageField(upload_to='media')
    bilnumber = models.CharField(max_length=10, blank=True, null=True)  # Allow null and blank
    bondnumber = models.CharField(max_length=10, blank=True, null=True)  # Allow null and blank



    def __str__(self):
        return self.fname





class Interestandpayment(models.Model):

    interestpaymentt_uuid = models.CharField(max_length=200,default=True)
    interestpaid = models.FloatField()
    paymentpaid = models.FloatField()
    datess = models.DateField()
