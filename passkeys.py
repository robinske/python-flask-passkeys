import json
import os
import requests

from dotenv import load_dotenv
from datetime import datetime
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

def _authenticators():
    with open('authenticators.json') as f:
        return json.load(f)
    
def _authenticator_by_aaguid(authenticators, aaguid):
    name = authenticators.get(aaguid, {}).get('name', 'Unknown Authenticator')
    return name

# GET routes
# Returns json

def list_factors(username):
    response = _get(f'Factors?entity_identity={username}')
    authenticators = _authenticators()

    factors = sorted(response.json()['factors'], key=lambda y: y['date_created'], reverse=True)
    for factor in factors:
        if factor.get('status') == 'verified':
            aaguid = factor.get('binding', {}).get('authenticator_metadata', {}).get('AAGUID')
            factor['authenticator_name'] = _authenticator_by_aaguid(authenticators, aaguid)
        else:
            factor['authenticator_name'] = 'N/A'

        factor['date_created'] = datetime.strptime(factor['date_created'], "%Y-%m-%dT%H:%M:%SZ").strftime('%Y-%m-%d')

    return factors

def get_factor(factor_sid):
    response = _get(f'Factors/{factor_sid}')
    authenticators = _authenticators()
    factor = response.json()
    if factor.get('status') == 'verified':
        aaguid = factor.get('binding', {}).get('authenticator_metadata', {}).get('AAGUID')
        factor['authenticator_name'] = _authenticator_by_aaguid(authenticators, aaguid)
    else:
        factor['authenticator_name'] = 'N/A'
    return factor

# POST routes
# Returns (json, status_code)

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
                'discoverable_credentials': 'required',
                'user_verification': 'preferred'
            }
        }
    }

    response = _post('Factors', data)
    return response.json().get('config', {}).get('creation_request'), response.status_code
    
def verify_factor(data):
    response = _post('Factors/Verify', data)
    return response.json(), response.status_code
    
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
   
    if identity:
        data['entity'] = { "identity": identity }

    response = _post('Challenges', data)
    return response.json().get('details', {}).get('publicKey'), response.status_code

def verify_challenge(data):
    response = _post("Challenges/Verify", data)
    return response.json(), response.status_code

# DELETE routes
# Returns status_code

def delete_factor(factor_sid):
    url = f'{BASE_URL}/Factors/{factor_sid}'
    response = requests.delete(url, auth=TWILIO_AUTH)
    return response.status_code