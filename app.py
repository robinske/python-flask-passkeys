import json

from dotenv import load_dotenv
from flask import Flask, flash, jsonify, render_template, request, redirect, session, url_for
from passkeys import create_factor, list_factors, verify_factor, delete_factor, get_challenges, create_challenge, verify_challenge


def to_pretty_json(value):
    return json.dumps(value, sort_keys=True,
                      indent=4, separators=(',', ': '))


load_dotenv()
app = Flask(__name__)
app.secret_key = 'SUP3R_$ECRET'
app.jinja_env.filters['tojson_pretty'] = to_pretty_json


@app.route('/')
def index():
    return redirect(url_for('register'))


@app.route('/passkeys', methods=['GET'])
def factor_list():
    return render_template('factors.html', factors=list_factors())


@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


@app.route('/factors/create', methods=['POST'])
def factor_create():
    username = request.form['username']
    response = create_factor(username)
    
    if response.status_code == 201:
        session[username] = response.json().get('sid')
        public_key = response.json().get('config').get('creation_request')
        return jsonify(public_key), 201
    else:
        return jsonify(response.json()), 400
    

@app.route('/factors/verify', methods=['POST'])
def factor_verify():
    credential = request.json
    response = verify_factor(credential)

    return jsonify(response.json()), response.status_code


@app.route('/factors/delete', methods=['POST'])
def factor_delete():
    sid = request.form['sid']
    response = delete_factor(sid)
    flash(response['message'])
    return redirect(url_for('factor_list'))
        

@app.route('/login-attempts', methods=['GET'])
def challenge_list():
    challenges = get_challenges()
    return render_template('challenges.html', challenges=challenges)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/challenges/create', methods=['POST'])
def challenge_create():
    username = request.form['username']
    factor_sid = session.get(username)

    if factor_sid is None:
        return jsonify({'message': f'No registered passkey found for {username}'}), 400
    
    response = create_challenge(username, factor_sid)
    if response.status_code == 201:
        public_key = response.json().get('details').get('publicKey')
        return jsonify(public_key), 201
    else:
        return jsonify(response.json()), 400


@app.route('/challenges/verify', methods=['POST'])
def challenge_verify():
    credential = request.json
    response = verify_challenge(credential)
    return jsonify(response.json()), response.status_code
