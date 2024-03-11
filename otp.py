import os
import random

from dotenv import load_dotenv
from twilio.rest import Client


load_dotenv()
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
verification_sid = os.environ['VERIFY_SERVICE_SID']
client = Client(account_sid, auth_token)

def send(to):
    token = random.randint(100000, 999999)
    print(token)
    verification = client.verify.v2.services(verification_sid).verifications.create(
        to=to, channel='sms'
    )
    return verification.sid


def check(to, token):
    check = client.verify.v2.services(verification_sid).verification_checks.create(to=to, code=token)
    return check.status == 'approved'
    