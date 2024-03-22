from django.shortcuts import render,redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib import messages
from .models import CustomUser 
import random
from datetime import datetime,timedelta
import smtplib
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
import string
from django.views.decorators.cache import never_cache
from admin_side.models import *



@never_cache
def loginn(request):
    if 'email1' in request.session:
        return redirect('homepage')
    email=request.POST.get("email")
    password=request.POST.get("password")
    if request.method=='POST':    
        user = authenticate(username=email,password=password)       
        if user is not None:
            if user.is_listed and user.is_authenticated:
                login(request,user)
                request.session['email1']=user.email     
                return redirect('homepage')
            else:
                messages.error(request,'you are blocked....')
                return redirect('login')
        else:
            messages.error(request,'check email and password')
            return redirect('login')

    return render(request,'user_authentication/login.html')


@never_cache
def signup(request):
    if 'email1' in request.session:
        return redirect('homepage')
    
    full_name=request.POST.get('fullname')
    email=request.POST.get('email')
    phone_number=request.POST.get('phonenumber')
    password=request.POST.get('password')
    confirm_password=request.POST.get('confirm_password')
    referal_code=request.POST.get('referal_code')
    if request.method=='POST':
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request,'email already taken')
        elif CustomUser.objects.filter(phone_number=phone_number).exists():
            messages.info(request,'Phone number is already taken')
        elif len(password)<6:
            messages.warning(request,'password length must be greater than 6')
        elif confirm_password != password:
            messages.success(request,'passwords does not matches')
        else:
            ref=string.digits + string.ascii_uppercase
            refferal = ''.join(random.choice(ref) for i in range(6))
            CustomUser.objects.create_user(full_name=full_name,email=email,phone_number=phone_number,password=password,username=email,referal_code=refferal)
            request.session['recipient_email']=email
            if referal_code !='':
                try:
                    person=CustomUser.objects.get(referal_code=referal_code)
                except:
                    person=None
                if person != None:
                    last=Wallet.objects.filter(user=person).all().order_by('-date').first()
                    balance=float(last.balance)+float(100)
                    new=Wallet(user=person,amount=100.00,balance=balance,transaction_method='Referal',transaction_type='credit')
                    new.save()
                    
                    obj=CustomUser.objects.filter(email=email).first()
                    balance=float(100)
                    secondperson=Wallet(user=obj,amount=100.00,balance=balance,transaction_method='Referal',transaction_type='credit')
                    secondperson.save()

            six_digit_otp(request)
            return redirect('otp')

    return render(request,'user_authentication/signup.html')

@never_cache
def six_digit_otp(request):
    # Generate a random 6-digit OTP
    otp=random.randint(100000,999999)
    request.session['otp1']=str(otp)

    expirationtime=datetime.now()+timedelta(seconds=35)
    request.session['expirationtime']=expirationtime.strftime("%Y-%m-%d %H:%M:%S")
    
    
    #send otp via email
    subject = 'Your 6-digit OTP for email verification'
    message = f'Your Cycle Hub Email Verification OTP:\n\n {otp}\n\nPlease keep this code confidential.\nThank you for choosing CycleHub.\nSincerely, The CycleHub Team'
    from_email = 'cyclehub578@gmail.com'
    recipient_email = request.session.get('recipient_email')
    recipient_list = [recipient_email]

    send_mail(subject,message,from_email,recipient_list,fail_silently=False)
    request.session['otpsecond']=30
    return redirect('otp')


@never_cache
def otp_verification(request):
    
    expirationtime=request.session.get('expirationtime')
    expire=datetime.strptime(expirationtime,"%Y-%m-%d %H:%M:%S")
    otp=request.POST.get('otp')
    otp1=request.session.get('otp1')
    email=request.session.get('recipient_email')
    m=CustomUser.objects.filter(email=email)[0]
    if request.method=='POST':
        if (datetime.now()<=expire and otp==otp1):
            m.is_listed=True
            m.save()
            return redirect('login')
        elif(datetime.now()<=expire and otp != otp1):
            messages.error(request,'invalid otp')
        else:
            messages.error(request,'time expired')
    
    return render(request,'user_authentication/otp.html',{'expiration_time': expirationtime})

@never_cache
def logoutt(request):
    request.session.flush()
    return redirect('homepage')