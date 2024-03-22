from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls import static
from django.contrib.auth.views import (
    LogoutView, 
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

urlpatterns = [
   path('login',views.loginn,name='login'),
   path('signup',views.signup,name='signup'),
   path('otp',views.otp_verification,name='otp'),
   path('otp_verification',views.six_digit_otp,name='getotp'),
   path('logoutt',views.logoutt,name='logoutt'),
   path('password-reset/', PasswordResetView.as_view(template_name='user_authentication/password_reset.html'),name='password-reset'),
   path('password-reset/done/', PasswordResetDoneView.as_view(template_name='user_authentication/password_reset_done.html'),name='password_reset_done'),
   path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='user_authentication/password_reset_confirm.html'),name='password_reset_confirm'),
   path('password-reset-complete/',PasswordResetCompleteView.as_view(template_name='user_authentication/password_reset_complete.html'),name='password_reset_complete'),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)