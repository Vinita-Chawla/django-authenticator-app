from django.db import models
from django.contrib.auth.models import AbstractUser

from django_rest_passwordreset.signals import reset_password_token_created
from django.dispatch import receiver
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags



# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


@receiver(reset_password_token_created)
def password_reset_token_created(reset_password_token, *args, **kwargs):
    sitelink = 'http://localhost:5173/'
    token = "?token={}".format(reset_password_token.key)
    full_link = str(sitelink)+str("reset-password")+str(token)

    print(full_link)
    print(token)

    context = {
        'full_link' : full_link,
        'email' : reset_password_token.user.email
    }

    html_message = render_to_string("backend/email.html", context=context)
    plain_message = strip_tags(html_message)
    email_address = reset_password_token.user.email

    msg = EmailMultiAlternatives(
        subject = "Request for resetting password for {title}".format(title=email_address),
        body = plain_message,
        from_email='sender@gmail.com',
        to=[email_address]
    )

    msg.attach_alternative(html_message, "text/html")
    msg.send()