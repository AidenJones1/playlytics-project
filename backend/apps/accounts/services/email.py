from django.core.mail import send_mail
from django.conf import settings

from apps.accounts.services.token import create_token

def send_activation_email(user_obj):
    token = create_token(user_obj)
    if settings.DEBUG:
        activation_link = f"http://127.0.0.1:8000/api/accounts/activate/{token}/"
    else:
        activation_link = f"{settings.FRONTEND_URL}/activate/{token}/"

    subject = "Activate Your Playlytics Account"
    message = f"Hi {user_obj.username},\n\nPlease click the link below to activate your Playlytics account:\n\n{activation_link}\n\nIf you did not create an account, please ignore this email.\n\nBest regards,\nThe Playlytics Team"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_obj.email]

    send_mail(subject, message, from_email, recipient_list)

def send_password_reset_email(user_obj):
    token = create_token(user_obj)
    if settings.DEBUG:
        print(f"Password reset token for {user_obj.username}:\n{token}")
    else:
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{token}/"
        subject = "Reset Your Playlytics Password"
        message = f"Hi {user_obj.username},\n\nPlease click the link below to reset your Playlytics password:\n\n{reset_link}\n\nIf you did not request a password reset, please ignore this email.\n\nBest regards,\nThe Playlytics Team"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user_obj.email]

        send_mail(subject, message, from_email, recipient_list)