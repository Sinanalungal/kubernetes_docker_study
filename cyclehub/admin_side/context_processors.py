from .models import ContactForm,OrderedItems
from django.utils import timezone

def mails(request):
    current_date_str = timezone.now().strftime('%Y-%m-%d')
    mail = ContactForm.objects.filter(time__startswith=current_date_str).all()
    count= mail.count()
    context = {
        'mails': mail,
        'count':count
    }
    return (context)

def notification(request):
    try:
        noti=OrderedItems.objects.all().order_by('-modified_time')[:5]
    except:
        noti=None
    return {'notification': noti ,'notcount':noti.count()}

