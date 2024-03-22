from django.urls import path
from .import views
# from django.conf import settings
# from django.conf.urls import static

urlpatterns = [
    path('',views.homepage,name='homepage'),
    path('shop/',views.shop,name='shop'),
    path('contact',views.contact,name='contact'),
    path('about',views.about,name='about'),
    path('wishlist',views.wishlist,name='wishlist'),
    path('cart',views.cartt,name='cart'),
    path('checkout',views.checkout,name='checkout'),
    path('product_detail/<str:id>',views.product_detail,name='product_detail'),
    path('get_variant_details/<int:variant_id>/', views.get_variant_details, name='get_variant_details'),    # path('filter_products/', views.filter_products, name='filter_products'),
    path('userprofile/',views.userprofile,name='userprofile'),
    path('add_address',views.add_address,name='add_address'),
    path('edit_address/<str:id>',views.edit_address,name='edit_address'),
    path('delete_address/<str:id>',views.delete_address,name='delete_address'),
    path('update_password',views.update_password,name='update_password'),
    path('update_user',views.update_user,name='update_user'),
    path('add_to_cart/',views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('quantitymanage/',views.quantitymanage,name='quantitymanage'),
    path('add_address1',views.add_address1,name='add_address1'),
    path('edit_address1/<str:id>',views.edit_address1,name='edit_address1'),
    path('orderconfirmation/',views.order_confirmation,name='orderconfirmation'),
    path('orderconfirmed',views.orderconfirmed,name='orderconfirmed'),
    path('order_management/<str:id>', views.order_management, name='order_management'),
    path('cancel_order/', views.cancel_order, name='cancel_order'),
    path('returnproduct',views.returnproduct,name='returnproduct'),
    path('wallet',views.wallets,name='wallet'),
    path('apply_coupon',views.apply_coupon,name='apply_coupon'),
    path('search',views.search,name='search'),
    path('wishlist_toggle/',views.wishlist_toggle,name='wishlist_toggle'),
    path('remove_from_wishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('invoice',views.invoice,name='invoice'),
    path('invoices/<str:id>',views.invoices,name='invoices'),
    path('order_page',views.order_page,name='order_page'),

]   

