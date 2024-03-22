from django.contrib import admin

# Register your models here.
from .models import *



admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(TyreSize)
admin.site.register(Product)
admin.site.register(Images)
admin.site.register(Cart)
admin.site.register(Orders)
admin.site.register(OrderedItems)
admin.site.register(Wallet)
admin.site.register(Couponuse)
admin.site.register(Wishlist)
admin.site.register(ContactForm)
admin.site.register(Banners)

