#################################  S E N D  O T P  C O D E  U S I N G  T W I L I O  #################################
import json
from django.conf import settings
from twilio.rest import Client
from asgiref.sync import sync_to_async

async def send_otp_via_twilio(mobile_number, otp_code):
    try:
        def _send_sms():
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body = f"Hi! Your OTP for verification is {otp_code}. It expires in 1 minutes. Keep it confidential. - Bagheera Carrom",
                messaging_service_sid=settings.TWILIO_MESSAGING_SERVICE_SID,
                to=f'+91{mobile_number}'
            )
            print(f"OTP sent successfully: {message.sid}")
            return True
        return await sync_to_async(_send_sms)()
    except Exception as e:
        print(f"Error sending OTP via Twilio: {e}")
        return False