from django.db import models
from user_authentication.models import *
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import user_passes_test 
from django.core.mail import send_mail
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings


class Category(models.Model):
    category_name = models.CharField(max_length=200)
    description = models.TextField()
    category_offer=models.DecimalField(max_digits=10, decimal_places=2,default=0)
    is_listed = models.BooleanField(default=False)

    def __str__(self):
        return self.category_name

class Brand(models.Model):
    brand_name = models.CharField(max_length=200)
    description = models.TextField()
    is_listed = models.BooleanField(default=False)

    def __str__(self):
        return self.brand_name


class Product(models.Model):
    product_name = models.CharField( max_length=200,blank=False,null=False)
    product_offer=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    description = models.TextField()
    brand_id = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_listed = models.BooleanField(default=False)

    def __str__(self):
        return self.product_name
    

class TyreSize(models.Model):
    tyre_size = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_id = models.ForeignKey(Product,on_delete=models.CASCADE) 
    stock=models.PositiveIntegerField(default=0)
    is_listed = models.BooleanField(default=False)
 
    def __str__(self):
        return str(self.tyre_size)


class Images(models.Model):
    image=models.ImageField(upload_to='product_images/',null=True,blank=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    def __str__(self):
        return f'Images for {self.product_id.product_name}'
    

class Cart(models.Model):
    tyresize_id=models.ForeignKey(TyreSize,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField()
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    total=models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f'cart {self.tyresize_id} of {self.tyresize_id.product_id.product_name}'
    
class Orders(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    order_id=models.CharField(unique=True)
    address=models.ForeignKey(Address,on_delete=models.CASCADE)
    fullproducttotal=models.DecimalField(max_digits=10, decimal_places=2)
    remainingbalance=models.DecimalField(max_digits=10, decimal_places=2)
    payment_method=models.CharField(max_length=200)
    order_date=models.DateTimeField(auto_now_add=True)
    expected_delivery=models.DateField(null=True,blank=True)
    delivery_date=models.DateField(null=True,blank=True)

    def __str__(self):
        return f"order details of {self.user}"
    
class OrderedItems(models.Model):
    order=models.ForeignKey(Orders,on_delete=models.CASCADE,related_name='ordered_items')
    tyrevariant=models.ForeignKey(TyreSize,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField()
    price=models.DecimalField(max_digits=10, decimal_places=2)
    payment_status=models.CharField(max_length=200,default="Pending")
    status=models.CharField(max_length=100,default='Order Confirmed')
    modified_time=models.DateTimeField(auto_now=True)
    date=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"ordered items of {self.tyrevariant}"
    

class Wallet(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    date=models.DateTimeField(auto_now_add=True)
    amount=models.DecimalField(max_digits=10, decimal_places=2)
    balance=models.DecimalField(max_digits=10, decimal_places=2)
    transaction_method=models.CharField(max_length=50)
    transaction_type=models.CharField(max_length=50)

class Coupons(models.Model):
    coupon_code=models.CharField(max_length=50)
    coupon_title=models.CharField(max_length=100)
    discount=models.DecimalField(max_digits=10, decimal_places=2)
    discount_type=models.CharField(max_length=50)
    valid_from=models.DateField(null=True,blank=True)
    valid_to=models.DateField(null=True,blank=True)
    quantity=models.PositiveIntegerField()
    usage_count=models.PositiveIntegerField(default=0)
    minimum_order=models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    is_listed=models.BooleanField(default=False)
    def __str__(self):
        return self.coupon_code

class Couponuse(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    coupon=models.ForeignKey(Coupons,on_delete=models.CASCADE)
    recieved_at=models.DateTimeField(auto_now_add=True)


class Wishlist(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)


class ContactForm(models.Model):
    # user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    full_name=models.CharField(max_length=100)
    email=models.EmailField()
    phone_number=models.CharField(max_length=15)
    message=models.TextField()
    time=models.CharField(max_length=100)
    def __str__(self):
        return f'message of {self.full_name}'
    
@receiver(post_save, sender=ContactForm)
def sendmail(sender, instance, **kwargs):
    subject = 'Form Submitted to CycleHub'
    message = f'Hi "{instance.full_name}".A form is submitted has been Submitted in CycleHub.We will connect with you as soon as possible.Thank You...'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [instance.email] 
    send_mail(subject, message, from_email, recipient_list)


class Banners(models.Model):
    image=models.ImageField(upload_to='banner_images/',null=True,blank=True)
    header=models.CharField(max_length=100,null=False,blank=False)
    is_listed=models.BooleanField(default=False)
    def __str__(self):
        return self.header