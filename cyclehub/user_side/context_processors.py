from admin_side.models import *


def s(request):
    try:
        cat=Category.objects.filter(is_listed=True).all().order_by('id')
    except:
        cat=None
    return { 's':cat }

