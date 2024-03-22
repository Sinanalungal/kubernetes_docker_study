from django.shortcuts import render, get_object_or_404, redirect
from admin_side.models import *
from user_authentication.models import *
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.db.models import Count
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from admin_side.models import Cart
from django.utils import timezone
from django.db.models import Max
import uuid
from datetime import datetime, timedelta, date
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import F


@never_cache
def homepage(request):
    k = Product.objects.filter(is_listed=True, tyresize__is_listed=True).annotate(tyresize_count=Count('tyresize')).filter(
            tyresize_count__gt=0).prefetch_related('tyresize_set', 'images_set').all().order_by('id')
    s = Category.objects.filter(is_listed=True).all().order_by('id')
    banners = Banners.objects.filter(is_listed=True).all()
    return render(request, 'user_side/index.html', {'k': k, 's': s, 'banners': banners})


@never_cache
def shop(request):
    category = request.GET.get('categories_id', '0')
    brand = request.GET.get('brand_id', '0')
    pricerange = int(request.GET.get('price_range', '100'))
    price = ((pricerange*20000)/100)
    if category == '0' and brand == '0':
        k = Product.objects.filter(is_listed=True, tyresize__is_listed=True).annotate(tyresize_count=Count('tyresize')).filter(
            tyresize_count__gt=0).filter(tyresize__offer_price__lt=price).prefetch_related('tyresize_set', 'images_set').all().order_by('id')
    elif category == '0':
        k = Product.objects.filter(is_listed=True, brand_id=brand, tyresize__is_listed=True).annotate(tyresize_count=Count(
            'tyresize')).filter(tyresize__offer_price__lt=price).prefetch_related('tyresize_set', 'images_set').all().order_by('id')
    elif brand == '0':
        k = Product.objects.filter(is_listed=True, category_id=category, tyresize__is_listed=True).annotate(tyresize_count=Count(
            'tyresize')).filter(tyresize__offer_price__lt=price).prefetch_related('tyresize_set', 'images_set').all().order_by('id')
    else:
        k = Product.objects.filter(is_listed=True, category_id=category, brand_id=brand, tyresize__is_listed=True).annotate(tyresize_count=Count(
            'tyresize')).filter(tyresize__offer_price__lt=price).prefetch_related('tyresize_set', 'images_set').all().order_by('id')

    paginator = Paginator(k, 9)
    page = request.GET.get('page')

    try:
        k = paginator.page(page)
    except PageNotAnInteger:
        k = paginator.page(1)
    except EmptyPage:
        k = paginator.page(paginator.num_pages)

    s = Category.objects.filter(is_listed=True).all().order_by('id')
    b = Brand.objects.filter(is_listed=True).all().order_by('id')
    return render(request, 'user_side/product.html', {'k': k, 's': s, 'b': b})


@never_cache
def contact(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        phonenumber = request.POST.get('phonenumber')
        message = request.POST.get('message')

        if fullname != '' and email != '' and phonenumber != '' and message != '':
            form = ContactForm(full_name=fullname, email=email,
                               phone_number=phonenumber, message=message, time=datetime.now())
            form.save()
            return JsonResponse({'success': True, 'message': 'Contact Form Submitted!'})
        else:
            return JsonResponse({'success': False, 'message': 'Contact Form not Submitted!'})
    return render(request, 'user_side/contact.html')


@never_cache
def about(request):
    return render(request, 'user_side/about.html')


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def wishlist(request):
    wishlist = Wishlist.objects.filter(user=request.user).all().order_by('id')
    return render(request, 'user_side/wishlist.html', {'wishlist': wishlist})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def cartt(request):
    m = Cart.objects.filter(user=request.user).order_by('id')
    k = Cart.objects.filter(
        user=request.user, tyresize_id__stock__gt=0).values_list('total', flat=True)
    total = sum(k)
    return render(request, 'user_side/cart.html', {'m': m, 'total': total})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def checkout(request):
    k = Cart.objects.filter(
        user=request.user, tyresize_id__stock__gt=0).values_list('total', flat=True)
    total = sum(k)
    products = Cart.objects.filter(
        user=request.user, tyresize_id__stock__gt=0).all()
    addresses = Address.objects.filter(
        user_id=request.user, is_listed=True).all()
    available_coupons = Coupons.objects.filter(
        is_listed=True, usage_count__lt=F('quantity')).all()
    context = {'products': products, 'total': total, 'razortotal': total*100,
               'address': addresses, 'available_coupons': available_coupons, 'today_date': date.today()}
    return render(request, 'user_side/checkout.html', context)


@never_cache
def product_detail(request, id):
    k = Product.objects.filter(is_listed=True, id=id).prefetch_related(
        'tyresize_set', 'images_set').first()
    return render(request, 'user_side/detail.html', {'k': k})


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def get_variant_details(request, variant_id):

    size_variant = get_object_or_404(TyreSize, id=variant_id)

    variant_details = {
        'price': size_variant.price,
        'offer_price': size_variant.offer_price,
        'stock': size_variant.stock,
    }
    return JsonResponse(variant_details)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def userprofile(request):
    addresses = Address.objects.filter(
        user_id=request.user, is_listed=True).all()
    return render(request, 'user_side/user_profile.html', {'addresses': addresses})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def add_address(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        address1 = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        user1 = request.user
        Address.objects.create(full_name=full_name, phone_number=phone_number,
                               address=address1, city=city, state=state, pincode=pincode, user_id=user1)
        return redirect('userprofile')
    else:
        return redirect('userprofile')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def edit_address(request, id):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        address1 = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        user1 = request.user
        m = Address(id=id, full_name=full_name, phone_number=phone_number,
                    address=address1, city=city, state=state, pincode=pincode, user_id=user1)
        m.save()
        return redirect('userprofile')
    else:
        return redirect('userprofile')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def delete_address(request, id):
    if request.method == 'POST':
        m = Address.objects.filter(id=id).first()
        m.is_listed = False
        m.save()
        return redirect('userprofile')
    else:
        return redirect('userprofile')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def update_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        user = authenticate(username=request.user.email,
                            password=current_password)
        if user is not None:
            if new_password == confirm_password and current_password != new_password:
                user.set_password(new_password)
                user.save()
        return redirect('userprofile')
    else:
        return redirect('userprofile')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def update_user(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')

        if full_name != '':
            request.user.full_name = full_name
            request.user.save()

            if phone != request.user.phone_number:
                request.user.phone_number = phone
                request.user.save()
        return redirect('userprofile')
    else:
        return redirect('userprofile')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def add_to_cart(request):
    if request.method == 'POST':
        tyresize_id = request.POST.get('tyresize_id')
        quantity = request.POST.get('quantity', 1)

        if tyresize_id and quantity:
            tyre_size = TyreSize.objects.filter(id=tyresize_id).first()

            if tyre_size:
                if tyre_size.stock > 0:
                    existing_item = Cart.objects.filter(
                        tyresize_id=tyresize_id, user=request.user).first()

                    if existing_item:
                        return JsonResponse({'error': 'Item already in the cart'})
                    else:
                        cart_item = Cart(tyresize_id=tyre_size, quantity=quantity,
                                         total=tyre_size.offer_price, user=request.user)
                        cart_item.save()
                        return JsonResponse({'message': 'Item added to cart'})
                else:
                    return JsonResponse({'error': 'Item is out of stock'})
            else:
                return JsonResponse({'error': 'Invalid TyreSize ID'})
        else:
            return JsonResponse({'error': 'Invalid data received'})
    else:
        return redirect('homepage')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def remove_from_cart(request):
    if request.method == 'POST':
        cart_id = request.POST.get("cart_id")
        try:
            cart_item = Cart.objects.get(user=request.user, id=cart_id)
            cart_item.delete()
            k = Cart.objects.filter(
                user=request.user, tyresize_id__stock__gt=0).values_list('total', flat=True)
            total = (sum(k))
            return JsonResponse({"message": "Item removed successfully", 'total': total})
        except Cart.DoesNotExist:
            return JsonResponse({"message": "Item not found"}, status=404)
    else:
        return redirect('cart')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def quantitymanage(request):
    if request.method == 'POST':
        id = int(request.POST.get('id'))
        variant = request.POST.get('variantId')

        if id == 1:
            c = Cart.objects.filter(id=variant).first()
            stock = c.tyresize_id.stock
            m = Cart.objects.filter(user=request.user, id=variant).first()
            quantity = m.quantity
            if int(quantity) < int(stock):
                m.quantity += 1
                m.save()
            else:
                stock = m.tyresize_id.stock
                m.quantity = stock
                m.save()
        else:
            c = Cart.objects.filter(id=variant).first()
            stock = c.tyresize_id.stock
            m = Cart.objects.filter(user=request.user, id=variant).first()
            quantity = m.quantity

            if int(quantity) > 1:
                m.quantity -= 1
                m.save()
            else:
                m.quantity = 1
                m.save()

        price = Cart.objects.filter(
            user=request.user, id=variant).first().tyresize_id.offer_price
        quantity = m.quantity
        m.total = price * quantity
        m.save()

        k = Cart.objects.filter(
            user=request.user, tyresize_id__stock__gt=0).values_list('total', flat=True)
        total = sum(k)
        return JsonResponse({'latestquantity': m.quantity, 'producttotal': m.total, 'total': total})
    else:
        return redirect('cart')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def add_address1(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        address1 = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        user1 = request.user
        Address.objects.create(full_name=full_name, phone_number=phone_number,
                               address=address1, city=city, state=state, pincode=pincode, user_id=user1)
        return redirect('checkout')
    # else:
    return render(request, 'user_side/add_address.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def edit_address1(request, id):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        address1 = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        user1 = request.user
        m = Address(id=id, full_name=full_name, phone_number=phone_number,
                    address=address1, city=city, state=state, pincode=pincode, user_id=user1)
        m.save()
        return redirect('checkout')
    else:
        return redirect('homepage')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def order_confirmation(request):
    if request.method == 'POST':
        address1 = request.POST.get('address_id')
        code = request.POST.get('code').strip()
        payment_method = request.POST.get('payment_method')
        unique_id = ((str(uuid.uuid4()))[:8]).upper()
        request.session['unique_id'] = unique_id
        fulltotal = 0
        if payment_method == "Cash On Delivery":
            if Cart.objects.filter(user=request.user):
                a = Address.objects.filter(id=address1).first()
                for i in Cart.objects.filter(user=request.user).all():
                    if i.tyresize_id.stock < i.quantity:
                        cart_url = reverse('cart')
                        response_data = {
                            'success': False, 'message': 'The stock is less than the quantity', 'redirect': cart_url}
                        return JsonResponse(response_data)
                m = Orders(user=request.user, order_id=unique_id, address=a, payment_method=payment_method, expected_delivery=datetime.now(
                ) + timedelta(days=7), fullproducttotal=fulltotal, remainingbalance=fulltotal)
                m.save()
                for i in Cart.objects.filter(user=request.user, tyresize_id__stock__gt=0).all():
                    producttotal = i.tyresize_id.offer_price * i.quantity
                    s = OrderedItems(
                        order=m, tyrevariant=i.tyresize_id, quantity=i.quantity, price=producttotal)
                    s.save()
                    fulltotal += producttotal
                    j = TyreSize.objects.filter(id=i.tyresize_id.pk).first()
                    j.stock -= i.quantity
                    j.save()
                m.fullproducttotal = fulltotal
                m.remainingbalance = fulltotal
                m.save()
                if code == '':
                    pass
                else:
                    try:
                        coupon = Coupons.objects.get(coupon_code=code)
                        obj = CustomUser.objects.filter(
                            email=request.user.email).first()

                        if not (Couponuse.objects.filter(user=obj, coupon=coupon).exists()) and coupon.usage_count < coupon.quantity and m.fullproducttotal >= coupon.minimum_order and coupon.valid_from <= timezone.now().date() <= coupon.valid_to and coupon.is_listed == True:
                            use = Couponuse(user=obj, coupon=coupon)
                            use.save()
                            coupon.usage_count += 1
                            coupon.save()
                            if coupon.discount_type == 'price':
                                m.fullproducttotal = m.fullproducttotal-coupon.discount
                                m.remainingbalance = m.remainingbalance-coupon.discount
                                m.save()
                            elif coupon.discount_type == 'percentage':
                                m.fullproducttotal = m.fullproducttotal - \
                                    (coupon.discount*(m.fullproducttotal/100))
                                m.remainingbalance = m.remainingbalance - \
                                    (coupon.discount*(m.fullproducttotal/100))

                                m.save()
                            else:
                                pass

                    except ValueError:
                        pass
                Cart.objects.filter(user=request.user).delete()
                order_confirmed_url = reverse('orderconfirmed')
                response_data = {'success': True,
                                 'redirect': order_confirmed_url}
                return JsonResponse(response_data)
        elif payment_method == 'RazorPay':
            if Cart.objects.filter(user=request.user):
                a = Address.objects.filter(id=address1).first()
                for i in Cart.objects.filter(user=request.user).all():
                    if i.tyresize_id.stock < i.quantity:
                        cart_url = reverse('cart')
                        response_data = {
                            'success': False, 'message': 'The stock is less than the quantity', 'redirect': cart_url}
                        return JsonResponse(response_data)
                m = Orders(user=request.user, order_id=unique_id, address=a, payment_method=payment_method, expected_delivery=datetime.now(
                ) + timedelta(days=7), fullproducttotal=fulltotal, remainingbalance=fulltotal)
                m.save()
                for i in Cart.objects.filter(user=request.user, tyresize_id__stock__gt=0).all():
                    producttotal = i.tyresize_id.offer_price * i.quantity
                    s = OrderedItems(order=m, tyrevariant=i.tyresize_id,
                                     quantity=i.quantity, price=producttotal, payment_status='Success')
                    s.save()
                    fulltotal += producttotal
                    j = TyreSize.objects.filter(id=i.tyresize_id.pk).first()
                    j.stock -= i.quantity
                    j.save()
                m.fullproducttotal = fulltotal
                m.remainingbalance = fulltotal
                m.save()
                if code == '':
                    pass
                else:
                    try:
                        coupon = Coupons.objects.get(coupon_code=code)
                        obj = CustomUser.objects.filter(
                            email=request.user.email).first()

                        if not (Couponuse.objects.filter(user=obj, coupon=coupon).exists()) and coupon.usage_count < coupon.quantity and m.fullproducttotal >= coupon.minimum_order and coupon.valid_from <= timezone.now().date() <= coupon.valid_to and coupon.is_listed == True:
                            use = Couponuse(user=obj, coupon=coupon)
                            use.save()
                            coupon.usage_count += 1
                            coupon.save()
                            if coupon.discount_type == 'price':
                                m.fullproducttotal = m.fullproducttotal-coupon.discount
                                m.remainingbalance = m.remainingbalance-coupon.discount
                                m.save()
                            elif coupon.discount_type == 'percentage':
                                m.fullproducttotal = m.fullproducttotal - \
                                    (coupon.discount*(m.fullproducttotal/100))
                                m.remainingbalance = m.remainingbalance - \
                                    (coupon.discount*(m.fullproducttotal/100))
                                m.save()
                            else:
                                pass

                    except ValueError:
                        pass
                Cart.objects.filter(user=request.user).delete()
                order_confirmed_url = reverse('orderconfirmed')
                response_data = {'success': True,
                                 'redirect': order_confirmed_url}
                return JsonResponse(response_data)
        elif payment_method == 'Wallet':
            if Cart.objects.filter(user=request.user):
                try:
                    bal = Wallet.objects.filter(
                        user=request.user).all().order_by('-date').first().balance
                except:
                    bal = 0
                tot = 0
                a = Address.objects.filter(id=address1).first()
                for i in Cart.objects.filter(user=request.user).all():
                    producttotal = i.tyresize_id.offer_price * i.quantity
                    tot += producttotal
                    if i.tyresize_id.stock < i.quantity:
                        cart_url = reverse('cart')
                        response_data = {
                            'success': False, 'message': 'The stock is less than the quantity', 'redirect': cart_url}
                        return JsonResponse(response_data)
                if bal < tot:
                    response_data = {
                        'success': False, 'message': 'There is no enough money in wallet', }
                    return JsonResponse(response_data)
                m = Orders(user=request.user, order_id=unique_id, address=a, payment_method=payment_method, expected_delivery=datetime.now(
                ) + timedelta(days=7), fullproducttotal=fulltotal, remainingbalance=fulltotal)
                m.save()
                for i in Cart.objects.filter(user=request.user, tyresize_id__stock__gt=0).all():
                    producttotal = i.tyresize_id.offer_price * i.quantity
                    s = OrderedItems(order=m, tyrevariant=i.tyresize_id,
                                     quantity=i.quantity, price=producttotal, payment_status='Success')
                    s.save()
                    fulltotal += producttotal
                    j = TyreSize.objects.filter(id=i.tyresize_id.pk).first()
                    j.stock -= i.quantity
                    j.save()
                m.fullproducttotal = fulltotal
                m.remainingbalance = fulltotal
                m.save()
                try:
                    w = Wallet.objects.filter(user=request.user).all().order_by(
                        '-date').first().balance
                except:
                    w = 0

                if code == '':
                    pass
                else:
                    try:
                        coupon = Coupons.objects.get(coupon_code=code)
                        obj = CustomUser.objects.filter(
                            email=request.user.email).first()

                        if not (Couponuse.objects.filter(user=obj, coupon=coupon).exists()) and coupon.usage_count < coupon.quantity and m.fullproducttotal >= coupon.minimum_order and coupon.valid_from <= timezone.now().date() <= coupon.valid_to and coupon.is_listed == True:
                            use = Couponuse(user=obj, coupon=coupon)
                            use.save()
                            coupon.usage_count += 1
                            coupon.save()
                            if coupon.discount_type == 'price':
                                m.fullproducttotal = m.fullproducttotal-coupon.discount
                                m.remainingbalance = m.remainingbalance-coupon.discount
                                m.save()
                            elif coupon.discount_type == 'percentage':
                                m.fullproducttotal = m.fullproducttotal - \
                                    (coupon.discount*(m.fullproducttotal/100))
                                m.remainingbalance = m.remainingbalance - \
                                    (coupon.discount*(m.fullproducttotal/100))
                                m.save()
                            else:
                                pass

                    except ValueError:
                        pass
                if w > 0:
                    obj = CustomUser.objects.filter(
                        email=request.user.email).first()
                    balance = ((w)-(m.fullproducttotal))
                    new = Wallet(user=obj, amount=m.fullproducttotal, balance=balance,
                                 transaction_method="Wallet", transaction_type='debit')
                    new.save()
                Cart.objects.filter(user=request.user).delete()
                order_confirmed_url = reverse('orderconfirmed')
                response_data = {'success': True,
                                 'redirect': order_confirmed_url}
                return JsonResponse(response_data)
        else:
            pass
    else:
        return redirect('cart')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def orderconfirmed(request):
    uuid = request.session.get('unique_id')
    ord = Orders.objects.filter(order_id=uuid).first()
    order = OrderedItems.objects.filter(order=ord)
    return render(request, 'user_side/order_confirmation.html', {'order': order})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def order_page(request):
    m = Orders.objects.filter(user=request.user).annotate(
        max_ordered_item_id=Max('ordered_items__id')).order_by('-max_ordered_item_id')
    context = {
        'order': m,
    }

    return render(request, 'user_side/user_all_orders.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def order_management(request,id):
    m = Orders.objects.filter(user=request.user,id=id).annotate(
        max_ordered_item_id=Max('ordered_items__id')).order_by('-max_ordered_item_id')
    context = {
        'order': m,
    }

    return render(request, 'user_side/user_orders.html', context)


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def get_cart_data(request):

    # Adjust this based on your actual model
    cart_items = Cart.objects.filter(
        user=request.user, tyresize_id__stock__gt=0)
    updated_cart_data = []

    for item in cart_items:
        if item.tyresize_id.stock > 0:
            updated_cart_data.append({
                'id': item.id,
                'quantity': item.quantity,
                'total': item.total(),
            })

    total = sum(item['total'] for item in updated_cart_data)

    return JsonResponse({'total': total, 'items': updated_cart_data})


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def cancel_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order_item = get_object_or_404(OrderedItems, id=order_id)

        if order_item.status == "Order Cancelled":
            return JsonResponse({'status': 'error', 'message': 'Order already canceled'})

        m = TyreSize.objects.filter(id=order_item.tyrevariant.pk).first()
        m.stock += order_item.quantity
        m.save()
        order_item.status = "Order Cancelled"
        order_item.save()
        if order_item.order.payment_method == "Cash On Delivery":
            remain = Orders.objects.filter(id=order_item.order.pk).first()
            remain.remainingbalance -= order_item.price
            remain.save()
            order_item.payment_status = 'Failed'
            order_item.save()
        elif order_item.order.payment_method == 'RazorPay' or order_item.order.payment_method == 'Wallet':
            remain = Orders.objects.filter(id=order_item.order.pk).first()
            remain.remainingbalance -= order_item.price
            remain.save()
            order_item.payment_status = 'Refunded'
            order_item.save()
            try:
                w = Wallet.objects.filter(user=request.user).all().order_by(
                    '-date').first().balance
            except:
                w = 0
            obj = CustomUser.objects.filter(email=request.user.email).first()
            balance = ((w)+(order_item.price))
            new = Wallet(user=obj, amount=order_item.price, balance=balance,
                         transaction_method="Refund", transaction_type='credit')
            new.save()
        else:
            pass

        return JsonResponse({'status': 'success', 'message': 'Order canceled successfully'})
    else:
        return redirect('homepage')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def wishlist_toggle(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')

        m = get_object_or_404(Product, id=product_id)

        if not Wishlist.objects.filter(user=request.user, product=m).exists():
            created = Wishlist(
                user=request.user,
                product=m
            )
            created.save()
            return JsonResponse({'success': True, 'message': 'Product added to wishlist'})
        else:
            return JsonResponse({'success': False, 'message': 'Product is already in the wishlist'})
    else:
        return redirect('homepage')


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def returnproduct(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order_item = get_object_or_404(OrderedItems, id=order_id)

        if order_item.status == "Order Returned":
            return JsonResponse({'success': False, 'message': 'Order already returned'})

        m = TyreSize.objects.filter(id=order_item.tyrevariant.pk).first()
        m.stock += order_item.quantity
        m.save()
        ord = Orders.objects.filter(
            order_id=order_item.order.order_id, user=request.user).first()
        ord.remainingbalance = order_item.order.remainingbalance-order_item.price
        ord.save()
        order_item.status = "Order Returned"
        order_item.save()

        if order_item.order.payment_method == "Cash On Delivery":
            order_item.payment_status = 'Refunded'
            order_item.save()
            try:
                w = Wallet.objects.filter(user=request.user).all().order_by(
                    '-date').first().balance
            except:
                w = 0
            obj = CustomUser.objects.filter(email=request.user.email).first()
            balance = ((w)+(order_item.price))
            new = Wallet(user=obj, amount=order_item.price, balance=balance,
                         transaction_method="Refund", transaction_type='credit')
            new.save()
        elif order_item.order.payment_method == 'RazorPay' or order_item.order.payment_method == 'Wallet':
            order_item.payment_status = 'Refunded'
            order_item.save()
            try:
                w = Wallet.objects.filter(user=request.user).all().order_by(
                    '-date').first().balance
            except:
                w = 0
            obj = CustomUser.objects.filter(email=request.user.email).first()
            balance = ((w)+(order_item.price))
            new = Wallet(user=obj, amount=order_item.price, balance=balance,
                         transaction_method="Refund", transaction_type='credit')
            new.save()
        else:
            pass

        return JsonResponse({'success': True, 'message': 'Order returned successfully'})
    else:
        return redirect('homepage')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def wallets(request):
    if request.method == 'POST':
        money = request.POST.get('money')
        m = CustomUser.objects.filter(email=request.user.email).first()
        k = Wallet.objects.filter(user=m).all().order_by('id').last()
        if k:
            balance = float(k.balance) + float(money)
        else:
            balance = money

        w = Wallet(user=m, amount=money, balance=balance,
                   transaction_method='RazorPay', transaction_type='credit')
        w.save()
        response_data = {'success': True}
        return JsonResponse(response_data)
    m = CustomUser.objects.filter(email=request.user.email).first()
    try:
        detail = Wallet.objects.filter(user=m).all().order_by('-date')
    except:
        pass
    try:
        total = Wallet.objects.filter(
            user=m).all().order_by('-date').first().balance
    except:
        total = 0

    return render(request, 'user_side/wallet.html', {'detail': detail, 'total': total})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('appliedcoupon')

        tot = Cart.objects.filter(
            user=request.user).values_list('total', flat=True)

        tot = sum(tot)

        try:
            coupon = Coupons.objects.get(coupon_code=code)
            obj = CustomUser.objects.filter(email=request.user.email).first()

            if not (Couponuse.objects.filter(user=obj, coupon=coupon).exists()) and coupon.usage_count < coupon.quantity and coupon.minimum_order <= tot and coupon.valid_from <= timezone.now().date() <= coupon.valid_to and coupon.is_listed == True:
                if coupon.discount_type == 'price':
                    tot = tot-coupon.discount
                elif coupon.discount_type == 'percentage':
                    tot = tot-(tot*((coupon.discount)/100))
                else:
                    pass
                return JsonResponse({'success': True, 'message': 'Coupon applied successfully', 'tot': tot})
            elif (Couponuse.objects.filter(user=obj, coupon=coupon).exists()):
                return JsonResponse({'success': False, 'message': 'Coupon is Used', 'tot': tot})
            else:
                return JsonResponse({'success': False, 'message': 'Give a valid coupon code', 'tot': tot})

        except Coupons.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Give a Valid Coupon Code', 'tot': tot})
    else:
        return redirect('homepage')


def search(request):
    category = request.GET.get('categories_id', '0')
    brand = request.GET.get('brand_id', '0')
    pricerange = int(request.GET.get('price_range', '100'))
    price = ((pricerange * 20000) / 100)
    search_query = request.GET.get('search', '')

    if category == '0' and brand == '0':
        k = Product.objects.filter(
            is_listed=True, tyresize__is_listed=True,
            tyresize__offer_price__lt=price, product_name__icontains=search_query
        ).annotate(tyresize_count=Count('tyresize')).filter(tyresize_count__gt=0).prefetch_related('tyresize_set', 'images_set').all().order_by('id')
    elif category == '0':
        k = Product.objects.filter(
            is_listed=True, brand_id=brand, tyresize__is_listed=True,
            tyresize__offer_price__lt=price, product_name__icontains=search_query
        ).annotate(tyresize_count=Count('tyresize')).prefetch_related('tyresize_set', 'images_set').all().order_by('id')
    elif brand == '0':
        k = Product.objects.filter(
            is_listed=True, category_id=category, tyresize__is_listed=True,
            tyresize__offer_price__lt=price, product_name__icontains=search_query
        ).annotate(tyresize_count=Count('tyresize')).prefetch_related('tyresize_set', 'images_set').all().order_by('id')
    else:
        k = Product.objects.filter(
            is_listed=True, category_id=category, brand_id=brand, tyresize__is_listed=True,
            tyresize__offer_price__lt=price, product_name__icontains=search_query
        ).annotate(tyresize_count=Count('tyresize')).prefetch_related('tyresize_set', 'images_set').all().order_by('id')

    paginator = Paginator(k, 9)
    page = request.GET.get('page')

    try:
        k = paginator.page(page)
    except PageNotAnInteger:
        k = paginator.page(1)
    except EmptyPage:
        k = paginator.page(paginator.num_pages)

    s = Category.objects.filter(is_listed=True).all().order_by('id')
    b = Brand.objects.filter(is_listed=True).all().order_by('id')

    return render(request, 'user_side/search.html', {'k': k, 's': s, 'b': b})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def remove_from_wishlist(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')

        wishlist_product = Wishlist.objects.filter(
            user=request.user, product__id=product_id).first()

        if wishlist_product:
            wishlist_product.delete()

            response_data = {
                'message': 'Product removed from wishlist successfully.',
            }
            return JsonResponse(response_data)
        else:
            response_data = {
                'error': 'Product not found in the wishlist.',
            }
            return JsonResponse(response_data, status=400)
    else:
        return redirect('homepage')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')
def invoice(request):
    if request.user.is_authenticated:
        try:
            latest_order = Orders.objects.filter(
                user=request.user).order_by('-id').first()
        except:
            return redirect('homepage')
        context = {'latest_order': latest_order}
        return render(request, 'user_side/invoice.html', context)
    else:
        return redirect('homepage')
    


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(lambda u: u.is_authenticated, login_url='login')   
def invoices(request,id):
    if request.user.is_authenticated:
        try:
            latest_order = Orders.objects.filter(
                user=request.user,id=id).order_by('-id').first()
        except:
            return redirect('homepage')
        context = {'latest_order': latest_order}
        return render(request, 'user_side/invoice.html', context)
    else:
        return redirect('homepage')

