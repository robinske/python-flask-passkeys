import os
import requests

from dotenv import load_dotenv
from urllib.parse import urlparse


load_dotenv()
RELYING_PARTY_ID = os.environ['RP_ID']
RELYING_PARTY_NAME = os.environ['RP_NAME']

TWILIO_AUTH = (os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
BASE_URL = f'{os.environ["API_BASE_URL"]}/Services/{os.environ["VERIFY_SERVICE_SID"]}'


def list_factors():
    url = f'{BASE_URL}/Factors'
    response = requests.get(url, auth=TWILIO_AUTH)

    factors = sorted(
        filter(lambda x: x['status'] == 'verified', response.json()['factors']), 
        key=lambda y: y['date_created'], reverse=True)

    return factors

def create_factor(username):
    o = urlparse(RELYING_PARTY_ID)
    url = f'{BASE_URL}/Factors'

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
    url = f'{BASE_URL}/Factors/Verify'
    response = requests.post(url, auth=TWILIO_AUTH, json=data, headers={'Content-Type': 'application/json'})
    return response

def delete_factor(factor_sid):
    url = f'{BASE_URL}/Factors/{factor_sid}'
    response = requests.delete(url, auth=TWILIO_AUTH)
    return response.json()

def get_challenges():
    url = f'{BASE_URL}/Challenges'
    response = requests.get(url, auth=TWILIO_AUTH)

    challenges = sorted(response.json()['challenges'], key=lambda y: y['date_created'], reverse=True)
    return challenges
    
def create_challenge(identity, factor_sid):
    o = urlparse(RELYING_PARTY_ID)
    url = f'{BASE_URL}/Challenges'
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
    url = f'{BASE_URL}/Challenges/Verify'
    response = requests.post(url, auth=TWILIO_AUTH, json=data, headers={'Content-Type': 'application/json'})
    return response