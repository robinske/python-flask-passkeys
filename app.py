from flask import Flask, flash, render_template, request
import os

from dotenv import load_dotenv
from twilio.rest import Client


app = Flask(__name__)
app.secret_key = 'SUP3R_$ECRET'


load_dotenv()
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
verification_sid = os.environ['VERIFY_SERVICE_SID']
client = Client(account_sid, auth_token)

def send(to):
    msg = client.messages.create(to=to, from_=os.environ['TWILIO_SENDER_ID'], body="Your verification code is 582367\n\n@verify.ngrok.io #582367")
    return msg.sid
    # verification = client.verify.v2.services(verification_sid) \
    #     .verifications \
    #     .create(to=to, channel='sms')
    # return verification.sid


def check(to, code):
    # check = client.verify.v2.services(verification_sid) \
    #     .verification_checks \
    #     .create(to=to, code=code)
    # return check.status == 'approved'
    return True
    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_verification():
    phone_number = request.form['phone_number']

    send(phone_number)
    return render_template('check.html', phone_number=phone_number)

@app.route('/check', methods=['POST'])
def check_verification():
    code = request.form['code']
    approved = check("+12313576187", code)

    if approved:
        flash('Approved', 'success')
        return render_template('approved.html')
    else:
        flash('Invalid token', 'error')
        return render_template('check.html')
    