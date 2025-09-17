#################################  S E N D  E M A I L  #################################
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from asgiref.sync import sync_to_async

async def send_mails(email, content, subject, html):
    msg = EmailMultiAlternatives(subject, content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html, "text/html")
    await sync_to_async(msg.send)()
    return {"status": True,"message" :"Email sended successfully"}