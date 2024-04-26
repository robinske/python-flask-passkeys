import os
import requests

from dotenv import load_dotenv
from urllib.parse import urlparse


load_dotenv()
RELYING_PARTY_ID = os.environ['RP_ID']
RELYING_PARTY_NAME = os.environ['RP_NAME']

TWILIO_AUTH = (os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
BASE_URL = f'{os.environ["API_BASE_URL"]}/Services/{os.environ["VERIFY_SERVICE_SID"]}'


def _get(path):
    url = f'{BASE_URL}/{path}'
    return requests.get(url, auth=TWILIO_AUTH)

def _post(path, data):
    url = f'{BASE_URL}/{path}'
    return requests.post(url, auth=TWILIO_AUTH, json=data, headers={'Content-Type': 'application/json'})

def list_all_factors():
    response = _get('Factors')

    factors = sorted(
        filter(lambda x: x['status'] == 'verified', response.json()['factors']), 
        key=lambda y: y['date_created'], reverse=True)

    return factors

def list_factors(username):
    response = _get(f'Factors?entity_identity={username}')

    factors = sorted(
        filter(lambda x: x['status'] == 'verified', response.json()['factors']), 
        key=lambda y: y['date_created'], reverse=True)

    return factors

def create_factor(username, passkey_name):
    parsed = urlparse(RELYING_PARTY_ID)
    hostname = parsed.hostname

    data = {
        'friendly_name': passkey_name,
        'factor_type': 'passkeys',
        'entity': {
            'identity': username,
            'display_name': f'{username} - {passkey_name}',
        },
        'config': {
            'relying_party': {
                'id': hostname,
                'name': RELYING_PARTY_NAME,
                'origins': [RELYING_PARTY_ID, f"http://{hostname}"]
            },
            'authenticator_criteria': {
                'authenticator_attachment': 'platform',
                'discoverable_credentials': 'required', # TODO make this configurable
                'user_verification': 'preferred'
            }
        }
    }

    response = _post('Factors', data)
    return response
    

# TODO normalize what's being returned to data - e.g. response.json() over response
def verify_factor(data):
    response = _post('Factors/Verify', data)
    return response

def get_factor(factor_sid):
    response = _get(f'Factors/{factor_sid}')
    return response.json()
    
def create_challenge(identity=None):
    """Creates a new login challenge.
    
    Will use discoverable credentials if identity not provided
    Learn more: https://web.dev/articles/webauthn-discoverable-credentials
    """
    parsed = urlparse(RELYING_PARTY_ID)
    data = {
        "details": {
            "rpId": parsed.hostname,
            "userVerification": "preferred"
        }
    }
   
    # TODO - is there any benefit to passing in a Factor SID? 
    if identity:
        data['entity'] = { "identity": identity }

    response = _post('Challenges', data)
    return response

def verify_challenge(data):
    response = _post("Challenges/Verify", data)
    return response

def delete_factor(factor_sid):
    url = f'{BASE_URL}/Factors/{factor_sid}'
    response = requests.delete(url, auth=TWILIO_AUTH)
    return response