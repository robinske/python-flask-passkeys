import os
import requests

from dotenv import load_dotenv
from urllib.parse import urlparse


load_dotenv()
RELYING_PARTY_ID = os.environ['NGROK_URL']
RELYING_PARTY_NAME = 'Acme Inc'
VERIFY_SID = os.environ['VERIFY_SERVICE_SID']
BASE_URL = os.environ['PREVIEW_API_BASE_URL']
TWILIO_AUTH = (os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])


def list_factors():
    url = f'{BASE_URL}/Services/{VERIFY_SID}/Factors'
    response = requests.get(url, auth=TWILIO_AUTH)

    factors = sorted(
        filter(lambda x: x['status'] == 'verified', response.json()['factors']), 
        key=lambda y: y['date_created'], reverse=True)

    return factors


def create_factor(username):
    o = urlparse(RELYING_PARTY_ID)
    url = f'{BASE_URL}/Services/{VERIFY_SID}/Factors'

    data = {
        'friendly_name': f'{RELYING_PARTY_NAME} Passkey',
        'factor_type': 'passkeys',
        'entity': {
            'identity': username,
            'display_name': username,
        },
        'config': {
            'relying_party': {
                'id': o.hostname,
                'name': RELYING_PARTY_NAME,
                'origins': [RELYING_PARTY_ID, f"http://{o.hostname}"]
            }
        },
        'authenticator_criteria': {
            'authenticator_attachment': 'platform',
            'discoverable_credentials': 'preferred',
            'user_verification': 'preferred'
        }
    }

    response = requests.post(url, auth=TWILIO_AUTH, json=data, headers={'Content-Type': 'application/json'})
    return response
    
def verify_factor(data):
    url = f'{BASE_URL}/Services/{VERIFY_SID}/Factors/Verify'
    response = requests.post(url, auth=TWILIO_AUTH, json=data, headers={'Content-Type': 'application/json'})
    return response

def delete_factor(factor_sid):
    url = f'{BASE_URL}/Services/{VERIFY_SID}/Factors/{factor_sid}'
    response = requests.delete(url, auth=TWILIO_AUTH)
    return response.json()


def get_challenges():
    url = f'{BASE_URL}/Services/{VERIFY_SID}/Challenges'
    response = requests.get(url, auth=TWILIO_AUTH)

    challenges = sorted(response.json()['challenges'], key=lambda y: y['date_created'], reverse=True)
    return challenges
    
def create_challenge(identity, factor_sid):
    o = urlparse(RELYING_PARTY_ID)
    url = f'{BASE_URL}/Services/{VERIFY_SID}/Challenges'
    data = {
        "factor_sid": factor_sid,
        "entity": {
            "identity": identity
        },
        "details": {
            "rpId": o.hostname,
            "userVerification": "preferred"
        }
    }

    response = requests.post(url, auth=TWILIO_AUTH, json=data, headers={'Content-Type': 'application/json'})
    return response

def verify_challenge(data):
    url = f'{BASE_URL}/Services/{VERIFY_SID}/Challenges/Verify'
    response = requests.post(url, auth=TWILIO_AUTH, json=data, headers={'Content-Type': 'application/json'})
    return response