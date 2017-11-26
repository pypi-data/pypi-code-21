from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from templated_email import send_templated_mail

User = get_user_model()


@receiver(post_save, sender=User)
def save_user_account(sender, instance, created, raw, **kwargs):
    if not raw and not created and instance.account:
        instance.account.save()


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, raw, **kwargs):
    if not raw and created and settings.LP_ACCOUNTS_WELCOME_EMAIL_ENABLED:
        send_templated_mail(
            template_name=settings.LP_ACCOUNTS_WELCOME_EMAIL_TEMPLATE,
            from_email=settings.LP_ACCOUNTS_WELCOME_EMAIL_SENDER,
            recipient_list=[instance.email],
            context={
                'username': instance.username,
                'full_name': instance.get_full_name(),
                'signup_date': instance.date_joined
            },
        )
