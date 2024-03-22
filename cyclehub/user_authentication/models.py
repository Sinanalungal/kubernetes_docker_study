from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    full_name=models.CharField(max_length=100)
    email=models.EmailField()
    phone_number=models.CharField(max_length=15)
    referal_code=models.CharField(max_length=20)
    is_listed=models.BooleanField(default=False)
    
    def __str__(self):
        return self.email

class Address(models.Model):
    full_name=models.CharField(max_length=100)
    phone_number=models.CharField(max_length=15)
    address=models.TextField()
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    pincode=models.CharField(max_length=10)
    user_id=models.ForeignKey(CustomUser,null=False,blank=False,on_delete=models.CASCADE)
    is_listed=models.BooleanField(default=True)
    def __str__(self):
        return self.address