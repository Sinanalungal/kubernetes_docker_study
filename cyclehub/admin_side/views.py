from django.shortcuts import render, redirect
from user_authentication.models import CustomUser
from django.contrib import messages
from .models import *
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from datetime import datetime
from django.utils import timezone
from django.db.models import Count,Q
from datetime import timedelta
from django.shortcuts import render
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
import xlwt  



def get_year_range():
    today = timezone.now()

    # Get the first day of the current year
    start_of_year = today.replace(month=1, day=1)

    year_list = []

    # Iterate over the years from six years ago to the current year
    current_year = start_of_year.year - 6
    while current_year <= today.year:
        year_list.append(current_year)
        
        current_year += 1

    return year_list


def get_month_range():
    today = timezone.now()

    # Get the first day of the current year
    start_of_year = today.replace(month=1, day=1)

    month_list = []

    current_month = start_of_year
    while current_month <= today:
        month_list.append(current_month)
        
        # Move to the next month, handling December
        if current_month.month == 12:
            current_month = current_month.replace(year=current_month.year + 1, month=1)
        else:
            current_month = current_month.replace(month=current_month.month + 1)

    return month_list


def get_date_range():
    today = timezone.now()

    # Calculate the date 7 days ago
    seven_days_ago = today - timedelta(days=6)

    date_list = []

    current_date = seven_days_ago
    while current_date <= today:
        date_list.append(current_date.date())
        
        current_date += timedelta(days=1)

    return date_list

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def dashboard(request):
    sale=request.GET.get('sale')
    first=request.GET.get('first')

    
    if first == 'Day' :
        req=timezone.now().today().day
        nooforder = OrderedItems.objects.exclude(Q(status='Order Cancelled') | Q(status='Order Returned')).filter(date__day=req).distinct().values_list('order__pk', flat=True).count()
    
        fullproduct = Orders.objects.filter(order_date__day=req).values_list('remainingbalance', flat=True)
        revenue = sum(fullproduct)
    
        custome = Orders.objects.distinct('user').filter(user__is_superuser=False).filter(order_date__day=req).count()
    elif first == 'Month':
        req=timezone.now().today().month
        nooforder = OrderedItems.objects.exclude(Q(status='Order Cancelled') | Q(status='Order Returned')).filter(date__month=req).distinct().values_list('order__pk', flat=True).count()
    
        fullproduct = Orders.objects.filter(order_date__month=req).values_list('remainingbalance', flat=True)
        revenue = sum(fullproduct)
        
        custome = Orders.objects.distinct('user').filter(user__is_superuser=False).filter(order_date__month=req).count()
    elif first == 'Year':
        req=timezone.now().today().year
        nooforder = OrderedItems.objects.exclude(Q(status='Order Cancelled') | Q(status='Order Returned')).filter(date__year=req).distinct().values_list('order__pk', flat=True).count()
    
        fullproduct = Orders.objects.filter(order_date__year=req).values_list('remainingbalance', flat=True)
        revenue = sum(fullproduct)
        
        custome = Orders.objects.distinct('user').filter(user__is_superuser=False).filter(order_date__year=req).count()
    elif first == 'Total':
        nooforder = OrderedItems.objects.exclude(Q(status='Order Cancelled') | Q(status='Order Returned')).distinct().values_list('order__pk', flat=True).count()
    
        fullproduct = Orders.objects.values_list('remainingbalance', flat=True)
        revenue = sum(fullproduct)
        
        custome = Orders.objects.distinct('user').filter(user__is_superuser=False).count()
    else:
        pass
    wallet = Orders.objects.filter(payment_method='Wallet').aggregate(count_method=Count('payment_method'))
    RazorPay = Orders.objects.filter(payment_method='RazorPay').aggregate(count_method=Count('payment_method'))
    Cod = Orders.objects.filter(payment_method='Cash On Delivery').aggregate(count_method=Count('payment_method'))
    
    tot = wallet['count_method'] + RazorPay['count_method'] + Cod['count_method']
    
    sellproduct = {i.product_name: 0 for i in Product.objects.all()}
    
    for i in Product.objects.all():
        m = OrderedItems.objects.filter(tyrevariant__product_id__product_name=i.product_name).exclude(Q(status='Order Cancelled') | Q(status='Order Returned')).aggregate(count=Count('tyrevariant__product_id__product_name'))
        sellproduct[i.product_name] = m['count']
    
    mostsell = dict(sorted(sellproduct.items(), key=lambda item: item[1], reverse=True))
    mostlistval = list(mostsell.values())[:4]
    mostlistkey = list(mostsell.keys())[:4]
    
    
    
    wallet_percentage = (wallet['count_method'] / tot) * 100 if tot > 0 else 0
    RazorPay_percentage = (RazorPay['count_method'] / tot) * 100 if tot > 0 else 0
    Cod_percentage = (Cod['count_method'] / tot) * 100 if tot > 0 else 0

    catfilter={}
    for i in Category.objects.all():
        try:
            count=OrderedItems.objects.filter(tyrevariant__product_id__category_id=i).exclude(Q(status='Order Cancelled') | Q(status='Order Returned')).all().count()
        except:
            count=0
        catfilter[i]=count
    
    datas={}
    if sale=='Week':
        date_range = get_date_range()
       
        for i in date_range:
            count=OrderedItems.objects.filter(date__date=i).all().count()
            datas[i]=count
    elif sale == 'Month':
        month_range = get_month_range()
        for start_of_month in month_range:
            end_of_month = (start_of_month.replace(month=start_of_month.month + 1) 
                            if start_of_month.month < 12 
                            else start_of_month.replace(year=start_of_month.year + 1, month=1)
                        ).replace(day=1, hour=23, minute=59, second=59)
            count = OrderedItems.objects.filter(date__range=[start_of_month, end_of_month]).count()
            datas[start_of_month] = count
    elif sale=='Year':
        year_range=get_year_range()
        for i in year_range:
            count=OrderedItems.objects.filter(date__year=i).all().count()
            datas[i] = count

            
    context = {
        'wallet': wallet_percentage,
        'RazorPay': RazorPay_percentage,
        'Cod': Cod_percentage,
        'mostsell': mostsell,
        'mostlistval': mostlistval,
        'mostlistkey': mostlistkey,
        'nooforder': nooforder,
        'revenue': revenue,
        'customers': custome,
        'catfilterkey':list(catfilter.keys()),
        'catfilterval':list(catfilter.values()),
        'dataskey':list(datas.keys()),
        'datasval':list(datas.values())
    }

    return render(request, 'admin_side/adminpanel_dashboard.html', context)


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='admin_login')
def order(request):
    ord= Orders.objects.all().order_by('id')
    return render(request, 'admin_side/adminpanel_orders.html',{'orders':ord})
@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='admin_login')
def about_order(request,id):
    try:
        detail=Orders.objects.filter(id=id).first().ordered_items.all().order_by('id')
    except:
        detail=None
    return render(request,'admin_side/about_order.html',{'detail':detail })


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def singleorderproduct(request,id):
    order=OrderedItems.objects.filter(id=id).first()
    useremail=order.order.user.email
    try:
        fund=Orders.objects.filter(id=order.order.pk).first()
    except:
        pass
    if request.method=='POST':
        option=request.POST.get('options')
        order.status= option
        order.save()
        if order.order.payment_method=="Cash On Delivery":
            if option=="Order Delivered":
                order.payment_status='Success'
                order.save()
            elif option=="Order Cancelled" :
                pk=order.tyrevariant.pk
                m=TyreSize.objects.filter(pk=pk).first()
                m.stock += order.quantity
                m.save()
                remain=Orders.objects.filter(id=order.order.pk).first()
                remain.remainingbalance-=order.price
                remain.save()
                order.payment_status='Failed'
                order.save()
                
            elif option=="Order Returned":
                pk=order.tyrevariant.pk
                m=TyreSize.objects.filter(pk=pk).first()
                m.stock += order.quantity
                m.save()
                order.payment_status='Refunded'
                order.save() 
                obj=CustomUser.objects.filter(email=useremail).first()
                try:
                    w=Wallet.objects.filter(user=obj).all().order_by('-date').first().balance
                except:
                    w=0
                
                balance=((w)+(order.price))
                new=Wallet(user=obj,amount=order.price,balance=balance,transaction_method="Wallet",transaction_type='credit')
                new.save()
            else:
                pass
         
        elif order.order.payment_method=="RazorPay" or order.order.payment_method=='Wallet':
            if option=="Order Cancelled" or option=="Order Returned":
                pk=order.tyrevariant.pk
                m=TyreSize.objects.filter(pk=pk).first()
                m.stock += order.quantity
                m.save()
                order.payment_status='Refunded'
                order.save()  
                if option=="Order Cancelled":
                    fund.remainingbalance-=order.price
                    fund.save()
                obj=CustomUser.objects.filter(email=useremail).first()
                try:
                    w=Wallet.objects.filter(user=obj).all().order_by('-date').first().balance
                except:
                    w=0
                balance=((w)+(order.price))
                new=Wallet(user=obj,amount=order.price,balance=balance,transaction_method="Wallet",transaction_type='credit')
                new.save()   
            else:      
                order.payment_status='Success'
                order.save()
        else:
            pass
        
    statuses=['Order Confirmed','Order Shipped','Out for Delivery','Order Cancelled','Order Delivered','Order Returned']
    return render(request,'admin_side/singleorderproduct.html',{'order':order,'statuses':statuses})




@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='admin_login')
def products(request):
    p = Product.objects.filter(is_listed=True).prefetch_related('images_set').order_by('id')
    return render(request, 'admin_side/adminpanel_products.html', {'p': p})
@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def variants(request,id):
    m=TyreSize.objects.filter(product_id=Product.objects.filter(id=id).first()).all().order_by('id')
    b=Images.objects.filter(product_id=Product.objects.filter(id=id).first()).all().order_by('id')
    return render(request,'admin_side/variants.html',{'m':m,'pdtid':id,'b':b})
@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def add_variants(request,id):
    k=Product.objects.filter(id=id).first()
    tyresize=request.POST.get('tyresize')
    price = request.POST.get('price')
    offerprice=price
    stock=request.POST.get('stock')
    
    if request.method=='POST':
        try:
            price = float(price)
            offerprice = float(offerprice)
            stock = int(stock)
        except ValueError:
            messages.error(request, 'Invalid input for price, offer price, or stock')
            return redirect('add_variants', id=id)
        
        if TyreSize.objects.filter(tyre_size=tyresize,product_id=k).exists():
            messages.info(request,'This tyre size already exists')
            return redirect('add_variants',id=id)
        elif float(tyresize)<=0:
            messages.info(request,'give a valid tyre size')
            return redirect('add_variants',id=id)
        elif price<0:
            messages.error(request,'give a valid price')
            return redirect('add_variants',id=id)
        elif offerprice<0:
            messages.warning(request,'enter a valid offerprice')
            return redirect('add_variants',id=id)
        elif int(stock)<0:
            messages.success(request,'give a proper stock number')
            return redirect('add_variants',id=id)
        else:
            m=TyreSize(tyre_size=tyresize,price=price,offer_price=offerprice,product_id=k,stock=stock)
            m.save()
            
            if float(m.product_id.product_offer) >= float(m.product_id.category_id.category_offer):
                m.offer_price= float(m.price) - float(m.price/100) * float(m.product_id.product_offer)
                m.save()
            elif float(m.product_id.product_offer) <= float(m.product_id.category_id.category_offer):
                m.offer_price= float(m.price) - float(m.price/100) * float(m.product_id.category_id.category_offer)
                m.save()
            else:
                m.offer_price=offerprice
                m.save()
            return redirect('variants',id=id)
    return render(request,'admin_side/add_variants.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def edit_variants(request,id):
    m=TyreSize.objects.filter(id=id).first()
    tyresize=request.POST.get('tyresize')
    price = request.POST.get('price')
    offerprice=price
    stock=request.POST.get('stock')
    if request.method=='POST':
        try:
            price = float(price)
            offerprice = float(offerprice)
            stock = int(stock)
        except ValueError:
            messages.error(request, 'Invalid input for price, offer price, or stock')
            return redirect('edit_variants',id=id)
        
        if not TyreSize.objects.filter(id=id).exists():
            return redirect('variants',id=m.product_id.pk)
        elif TyreSize.objects.filter(tyre_size=tyresize,product_id=m.product_id.pk).exclude(id=id).exists():
            messages.info(request,'this tyresize already exists')
            return redirect('edit_variants',id=id)
        elif float(tyresize)<=0:
            messages.info(request,'give a valid tyre size')
            return redirect('edit_variants',id=id)
        elif price<0:
            messages.error(request,'give a valid price')
            return redirect('edit_variants',id=id)
        elif offerprice <0:
            messages.warning(request,'enter a valid offerprice')
            return redirect('edit_variants',id=id)
        elif int(stock) <0:
            messages.success(request,'give a proper stock number')
            return redirect('edit_variants',id=id)
        else:
            m.tyre_size=tyresize
            m.price=price
            m.offer_price=offerprice
            m.stock=stock
            m.save()
            

            if float(m.product_id.product_offer) >= float(m.product_id.category_id.category_offer):
                m.offer_price= float(m.price) - float(m.price/100) * float(m.product_id.product_offer)
                m.save()
            elif float(m.product_id.product_offer) <= float(m.product_id.category_id.category_offer):
                m.offer_price= float(m.price) - float(m.price/100) * float(m.product_id.category_id.category_offer)
                m.save()
            else:
                m.offer_price=offerprice
                m.save()


            return redirect('variants',id=m.product_id.pk)
    return render(request,'admin_side/edit_variants.html',{'m':m})
@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def add_products(request):
    
    c = Category.objects.all()
    b = Brand.objects.all()

    
    if request.method == 'POST':
        name = request.POST.get('productname')
        name=name.strip()
        name = name.lower()

        brand = request.POST.get('brand')
        description = request.POST.get('description')
        category = request.POST.get('category')
        additionalimages = request.FILES.getlist('images')

        if Product.objects.filter(product_name__iexact=name).exists():
            messages.error(request, 'this product is already exists')
            return redirect('add_products')
        elif name=='':
            messages.error(request,'name should not be null')
            return redirect('add_products')

        elif brand=='':
            messages.info(request,'choose a brand')
            return redirect('add_products')
        elif category=='':
            messages.success(request,'choose a category')
            return redirect('add_products')
        else:
            m = Product(product_name=name,description=description, brand_id=Brand.objects.filter(id=brand).first(), category_id=Category.objects.filter(id=category).first())
            m.save()
   
            
            if additionalimages:
                for image_file in additionalimages:
                    p = Images(product_id=m, image=image_file)
                    p.save()

             
            return redirect('products')
        
        
    return render(request, 'admin_side/add_products.html', {'c': c, 'b': b,})
@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def edit_products(request, id):
    c = Category.objects.all()
    b = Brand.objects.all()
    p = Product.objects.filter(id=id).first()

    if request.method=='POST':
        name = request.POST.get('productname')
        name=name.strip()
        name = name.lower()

        brand =request.POST.get('brand')
        description = request.POST.get('description')
        category = request.POST.get('category')
        
        if not Product.objects.filter(id=id).exists():
            messages.error(request, 'this product does not exists')
            return redirect('products')
        elif name=='':
            messages.error(request,'name should not be null')
            return redirect('edit_products',id=id)
        elif Product.objects.exclude(id=id).filter(product_name__iexact=name).exists():
            messages.error(request, 'this product name is already exists')
            return redirect('edit_products',id=id)

        elif brand=='':
            messages.info(request,'choose a brand')
            return redirect('edit_products',id=id)
        elif category=='':
            messages.success(request,'choose a category')
            return redirect('edit_products',id=id)
        else:
         
            p.product_name=name
          
            p.description=description
            p.brand_id=Brand.objects.filter(id=brand).first()
            p.category_id=Category.objects.filter(id=category).first()
            
            p.save()
            additionalimages = request.FILES.getlist('images')
            
            if additionalimages:

                
                for image_file in additionalimages:
                    new_image = Images(product_id=p, image=image_file)
                    new_image.save()
            
            
            return redirect('products')
    return render(request, 'admin_side/edit_products.html', {'j': p,'b':b,'c':c,})


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def users(request):
    u = CustomUser.objects.all().exclude(is_superuser=True).order_by('id')
    return render(request, 'admin_side/adminpanel_users.html', {'u': u})



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def categories(request):
    m = Category.objects.all().order_by('id')
    return render(request, 'admin_side/adminpanel_categories.html', {'m': m})



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def add_categories(request):
    categoryname = request.POST.get('categoryname')
    categorydescription = request.POST.get('categorydescription')
    if request.method == 'POST':
        categoryname=categoryname.strip()
        categoryname=categoryname.lower()
        categorydescription=categorydescription.strip()
        if Category.objects.filter(category_name=categoryname).exists():
            messages.error(request, 'category already exists')
            return redirect('add_categories')
        elif categoryname=='':
            messages.error(request,'Category cannot be null')
            return redirect('add_categories')
        else:
            p = Category.objects.create(
                category_name=categoryname, description=categorydescription)
            p.save()
            return redirect('categories')
    return render(request, 'admin_side/add_categories.html')


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def edit_categories(request,id):
    m=Category.objects.filter(pk=id).first()
    categoryname = request.POST.get('categoryname')

    categorydescription = request.POST.get('categorydescription')
    if request.method=='POST':
        categoryname=categoryname.strip()
        categoryname=categoryname.lower()
        categorydescription=categorydescription.strip()
        if not Category.objects.filter(id=id).exists():
            messages.error(request,'this category does not exists')
            return redirect('categories')
        elif categoryname=='':
            messages.error(request,'Category cannot be null')
            return redirect('edit_categories',id=id)
        elif Category.objects.exclude(id=id).filter(category_name=categoryname).exclude(id=id).exists():
            messages.error(request,'this category is already exists')
            return redirect('edit_categories',id=id)

        else:
            m.category_name=categoryname
            m.description=categorydescription
            m.save()
            return redirect('categories')
    return render(request, 'admin_side/edit_categories.html',{'m':m})


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def brands(request):
    m = Brand.objects.all().order_by('id')
    return render(request, 'admin_side/adminpanel_brands.html', {'m': m})


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def add_brands(request):
    brandname = request.POST.get('brandname')

    branddescription = request.POST.get('branddescription')
    if request.method == 'POST':
        brandname=brandname.strip()
        brandname=brandname.lower()
        branddescription=branddescription.strip()
        if Brand.objects.filter(brand_name=brandname).exists():
            messages.error(request, 'brand already exists')
            return redirect('add_brands')
        elif brandname=='':
            messages.error(request,'brand name cannot be null')
            return redirect('add_brands')
        else:
            m = Brand(
                brand_name=brandname, description=branddescription)
            m.save()
            return redirect('brands')
    return render(request, 'admin_side/add_brands.html')


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def edit_brands(request,id):
    m=Brand.objects.filter(pk=id).first()
    brandname = request.POST.get('brandname')

    branddescription = request.POST.get('branddescription')
    if request.method=='POST':
        brandname=brandname.strip()
        brandname=brandname.lower()
        branddescription=branddescription.strip()
        if not Brand.objects.filter(id=id).exists():
            messages.error(request,'this brand does not exists')
            return redirect('brands')
        elif brandname=='':
            messages.error(request,'brand name cannot be null')
            return redirect('edit_brands',id=id)
        elif Brand.objects.exclude(id=id).filter(brand_name=brandname).exclude(id=id).exists():
            messages.error(request,'this brand is already exists')
            return redirect('edit_brands',id=id)
        else:
            m.brand_name=brandname
            m.description=branddescription
            m.save()
            return redirect('brands')
    return render(request, 'admin_side/edit_brands.html',{'m':m})


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def coupons_view(request):
    m=Coupons.objects.all().order_by('id')
    return render(request, 'admin_side/adminpanel_coupons.html',{'m':m})


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def add_coupons(request):
    if request.method=='POST':
        couponcode=request.POST.get('couponcode')
        coupontitle=request.POST.get('coupontitle')
        discount=request.POST.get('discount')
        discount_method=request.POST.get('discountmethod')
        quantity=request.POST.get('quantity')
        min_order=request.POST.get('minimumorder')
        valid_from=request.POST.get('validfrom')
        valid_to=request.POST.get('validto')
        coup=[]
        for i in Coupons.objects.all():
            coup.append(i.coupon_code)
        if couponcode in coup:
            messages.error(request,'this coupon code is already exists.')
            return redirect('add_coupons')
        elif datetime.strptime(valid_from, '%Y-%m-%d').date() < timezone.now().date():
            messages.error(request,'give a valid date')
            return redirect('add_coupons')
        elif datetime.strptime(valid_from, '%Y-%m-%d').date() > datetime.strptime(valid_to, '%Y-%m-%d').date():
            messages.error(request,'check your valid upto date')
            return redirect('add_coupons')
        else:
            m=Coupons(coupon_code=couponcode,coupon_title=coupontitle,discount=discount,discount_type=discount_method,quantity=quantity,valid_from=valid_from,valid_to=valid_to,minimum_order=min_order)
            m.save()
            return redirect('coupons')
    return render(request, 'admin_side/add_coupons.html')


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def edit_coupon(request,id):
    m=Coupons.objects.filter(id=id).first()
    if request.method=='POST':
        couponcode=request.POST.get('couponcode')
        coupontitle=request.POST.get('coupontitle')
        discount=request.POST.get('discount')
        discount_method=request.POST.get('discountmethod')
        quantity=request.POST.get('quantity')
        min_order=request.POST.get('minimumorder')
        valid_from=request.POST.get('validfrom')
        valid_to=request.POST.get('validto')
        coup=[]
        for i in Coupons.objects.exclude(id=id).all():
            coup.append(i.coupon_code)
        if couponcode in coup:
            messages.error(request,'this coupon code is already exists.')
            return redirect('edit_coupon',id=id)
        elif datetime.strptime(valid_from, '%Y-%m-%d').date() < timezone.now().date():
            messages.error(request,'give a valid date')
            return redirect('edit_coupon',id=id)
        elif datetime.strptime(valid_from, '%Y-%m-%d').date() > datetime.strptime(valid_to, '%Y-%m-%d').date():
            messages.error(request,'check your valid upto date')
            return redirect('edit_coupon',id=id)
        else:
            m.coupon_code=couponcode
            m.coupon_title=coupontitle
            m.discount=discount
            m.discount_type=discount_method
            m.quantity=quantity
            m.valid_from=valid_from
            m.valid_to=valid_to
            m.minimum_order=min_order
            m.save()
            return redirect('coupons')
    return render(request,'admin_side/edit_coupon.html',{'m':m})

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def payment_method(request):
    return render(request, 'admin_side/adminpanel_payment.html')


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def deletecoupon(request,id):
    m=Coupons.objects.filter(id=id).first().delete()
    return redirect('coupons')


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def couponlist(request,id):
    m=Coupons.objects.filter(id=id).first()
    if m.is_listed==True:
        m.is_listed=False
        m.save()
    else:
        m.is_listed=True
        m.save()
    return redirect('coupons')



@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def banners(request):
    banners=Banners.objects.all()
    
    context={
        'banners':banners
    }
    return render(request, 'admin_side/adminpanel_banners.html',context)


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def add_banners(request):
    if request.method=='POST': 
        image=request.FILES.get('image')
        
        header=request.POST.get('header')
        header=header.strip()
        
        if header!='':
            banner=Banners(image=image,header=header)
            banner.save()
            return redirect('banners')
        else:
            return redirect('add_banners')
    
    return render(request, 'admin_side/add_banners.html')


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def trash(request):
    p = Product.objects.filter(is_listed=False).prefetch_related('images_set').order_by('id')
    return render(request, 'admin_side/adminpanel_trash.html', {'p': p})


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def user_controlling(request,id):
    m=CustomUser.objects.filter(id=id).first()
    if m.is_listed==True:
        m.is_listed=False
    else:
        m.is_listed=True
    
    m.save()
    return redirect('users')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def product_controlling(request,id):
    m=Product.objects.filter(id=id).first()
    if m.is_listed==True:
        m.is_listed=False
    else:
        m.is_listed=True
    
    m.save()
    return redirect('products')

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def product_controlling_tr(request,id):
    m=Product.objects.filter(id=id).first()
    if m.is_listed==True:
        m.is_listed=False
    else:
        m.is_listed=True
    
    m.save()
    return redirect('trash')

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def variant_controlling(request,id):
    m=TyreSize.objects.filter(id=id).first()
    if m.is_listed==True:
        m.is_listed=False
    else:
        m.is_listed=True
    
    m.save()
    return redirect('variants',id=m.product_id.pk)

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def category_controlling(request,id):
    m=Category.objects.filter(id=id).first()
    if m.is_listed==True:
        m.is_listed=False
    else:
        m.is_listed=True
    
    m.save()
    return redirect('categories')

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def brand_controlling(request,id):
    m=Brand.objects.filter(id=id).first()
    if m.is_listed==True:
        m.is_listed=False
    else:
        m.is_listed=True
    
    m.save()
    return redirect('brands')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login') 
def offers(request):
    return render(request,'admin_side/adminpanel_offers.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')  
def category_offer(request):
    c=Category.objects.all()
    return render(request,'admin_side/category_offers.html',{'c':c})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')
def product_offer(request):
    p=Product.objects.filter(is_listed=True).all()
    return render(request,'admin_side/product_offer.html',{'p':p})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')  
def edit_category_offer(request,id):
    c=Category.objects.filter(id=id).first()
    if request.method=='POST':
        offer=request.POST.get('offerinput')

        c.category_offer=offer
        c.save()
        
        for i in c.product_set.all():
            for j in i.tyresize_set.all():
                if float(offer) >= float(j.product_id.product_offer):
                    j.offer_price=float(j.price) - (float(j.price/100) * float(offer))
                    j.save()


        return redirect('category_offer')
    return render(request,'admin_side/edit_category_offer.html',{'c':c})



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')  
def edit_product_offer(request,id):
    p=Product.objects.filter(id=id).first()
    if request.method=='POST':
        offer=request.POST.get('offerinput')

        p.product_offer=offer
        p.save()
        for i in p.tyresize_set.all():
            if float(i.product_id.category_id.category_offer) <= float(offer):
                i.offer_price = float(i.price) - (float(i.price) * float(offer) / 100)
                i.save()


        return redirect('product_offer')
    return render(request,'admin_side/edit_product_offer.html',{'p':p})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_superuser, login_url='login')
def reports(request):
    frm = request.GET.get('from', '')
    to = request.GET.get('to', '')

    if frm == '':
        frm = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

    if to == '':
        to = datetime.now().strftime('%Y-%m-%d')

    request.session['from'] = frm
    request.session['to'] = to

    sales = Orders.objects.filter(order_date__date__gte=frm, order_date__date__lte=to).order_by('-order_date').all()
    stock = Product.objects.all()
    cancel = Orders.objects.filter(ordered_items__status__contains='Order Cancelled').distinct()

    context = {'sales': sales, 'stock': stock, 'cancel': cancel}
    return render(request, 'admin_side/reports.html', context)




def render_to_pdf(template_src, context_dict=None):
    if context_dict is None:
        context_dict = {}

    template = get_template(template_src)
    html = template.render(context_dict)

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')

    return None


from urllib.parse import quote


class DownloadPDF1(View):
    def get(self, request, *args, **kwargs):

        
        data = {'sales': Orders.objects.filter(order_date__date__gte=request.session.get('from'),order_date__date__lte=request.session.get('to')).order_by('-order_date').all(),'from':request.session.get('from'),'to':request.session.get('to')}
        pdf = render_to_pdf('admin_side/sales_report.html', data)

        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Sales_report_%s.pdf" % ("12341231")

        # Encode the filename using quote to handle special characters
        content = 'attachment; filename="%s"' % quote(filename)
        response['Content-Disposition'] = content

        return response
    

class DownloadPDF2(View):
    def get(self, request, *args, **kwargs):
        data = {'stock': Product.objects.all()}
        pdf = render_to_pdf('admin_side/stock_report.html', data)

        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Stock_report_%s.pdf" % ("12341231")

        # Encode the filename using quote to handle special characters
        content = 'attachment; filename="%s"' % quote(filename)
        response['Content-Disposition'] = content

        return response
   
class DownloadPDF3(View):
        def get(self, request, *args, **kwargs):
            data = {'cancel': Orders.objects.filter(ordered_items__status__contains='Order Cancelled').distinct()}
            pdf = render_to_pdf('admin_side/cancel_report.html', data)

            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Cancel_report_%s.pdf" % ("12341231")

            # Encode the filename using quote to handle special characters
            content = 'attachment; filename="%s"' % quote(filename)
            response['Content-Disposition'] = content

            return response


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u:u.is_superuser, login_url='login')        
def banner_controlling(request,id):
    m=Banners.objects.filter(id=id).first()
    if m.is_listed==True:
        m.is_listed=False
    else:
        m.is_listed=True
    
    m.save()
    return redirect('banners')    


# Download Exel
def download_exel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=SalesReport-'+ str(datetime.now())+'-.xls' 
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('SalesReport')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold=True
    columns = ['Order ID', 'User', 'Order Date', 'Products','Variant', 'Quantity', 'Price','Payment Method','Status']
    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num], font_style)
    
    font_style = xlwt.XFStyle()

    sales_from = request.session.get('from','')
    sales_to = request.session.get('to','')

    if not sales_from:
        sales_from = datetime.now() - timedelta(days=365)
    
    if not sales_to:
        sales_to = datetime.now()

    orders = Orders.objects.all().order_by('-order_date').filter(order_date__range=[sales_from, sales_to]).values_list('order_id','user__full_name','order_date__date','ordered_items__tyrevariant__product_id__product_name','ordered_items__tyrevariant__tyre_size','ordered_items__quantity','ordered_items__price','payment_method','ordered_items__status')

    for order in orders:
        row_num+=1
        for col_num in range(len(order)):
            ws.write(row_num,col_num,str(order[col_num]),font_style)

    wb.save(response)

    return response

def download_exel1(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=StockReport-'+ str(datetime.now())+'-.xls' 
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('SalesReport')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold=True
    columns = ['Product Name', 'Category', 'Brand', 'Tyre Sizes','Current Price', 'Stock']
    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num], font_style)
    
    font_style = xlwt.XFStyle()


    stocks = TyreSize.objects.all().values_list('product_id__product_name','product_id__category_id__category_name' ,'product_id__brand_id__brand_name', 'tyre_size', 'offer_price', 'stock')

    for stock in stocks:
        row_num+=1
        for col_num in range(len(stock)):
            ws.write(row_num,col_num,str(stock[col_num]),font_style)

    wb.save(response)

    return response


def download_exel2(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=CancelReport-'+ str(datetime.now())+'-.xls' 
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('SalesReport')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold=True
    columns = ['Order ID', 'User', 'Order Date', 'Products','Variant', 'Quantity', 'Price','Payment Method','Status']
    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num], font_style)
    
    font_style = xlwt.XFStyle()


    orders = Orders.objects.all().order_by('-order_date').filter(ordered_items__status__contains='Order Cancelled').values_list('order_id','user__full_name','order_date__date','ordered_items__tyrevariant__product_id__product_name','ordered_items__tyrevariant__tyre_size','ordered_items__quantity','ordered_items__price','payment_method','ordered_items__status')

    for order in orders:
        row_num+=1
        for col_num in range(len(order)):
            ws.write(row_num,col_num,str(order[col_num]),font_style)

    wb.save(response)

    return response

