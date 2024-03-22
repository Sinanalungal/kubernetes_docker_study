# from allauth.socialaccount.models import SocialAccount
# from allauth.account.signals import user_logged_in
# from django.dispatch import receiver

# @receiver(user_logged_in)
# def custom_save_profile(request, user, **kwargs):
#     # This function will be called when a user logs in.
#     # Access additional information using the SocialAccount model.
#     social_account = SocialAccount.objects.get(user=user)
#     extra_data = social_account.extra_data

#     # Extract and save additional fields to your user model
#     user.full_name = extra_data.get('given_name', '')
#     user.phone_number = extra_data.get('phone_number', '')
#     user.save()