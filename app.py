import json

from dotenv import load_dotenv
from flask import Flask, flash, jsonify, render_template, request, redirect, session, url_for
from passkeys import *
from ua_parser import user_agent_parser


load_dotenv()
app = Flask(__name__)
app.secret_key = 'SUP3R_$ECRET' # use a real secret here

def to_pretty_json(value):
    return json.dumps(value, sort_keys=True, indent=4, separators=(',', ': '))

def platform(ua_string):
    '''
    Turns 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    to 'Apple Mac OS X' 
    '''
    parsed = user_agent_parser.Parse(ua_string)
    return f"{parsed['device']['brand']} {parsed['os']['family']}"

app.jinja_env.filters['tojson_pretty'] = to_pretty_json

# View routes
@app.route('/')
def index():
    return redirect(url_for('factor_list'))

@app.route('/passkeys', methods=['GET'])
def factor_list():
    if not session.get('logged_in'):
        flash('You must be logged in to view Passkeys.', 'info')
        return redirect(url_for('login'))

    username = session.get('username')
    if not username:
        return render_template('factors.html', factors=[])

    return render_template('factors.html', factors=list_factors(username))

@app.route('/passkeys/<sid>', methods=['GET'])
def factor_detail(sid):
    if not session.get('logged_in'):
        flash('You must be logged in to view Passkeys.', 'info')
        return redirect(url_for('login'))

    factor = get_factor(sid)
    return render_template('factor.html', factor=factor)

@app.route('/register', methods=['GET'])
def register():
    return render_template('auth.html', submit="register")

@app.route('/login', methods=['GET'])
def login():
    if session.get('logged_in'):
        flash('You are already logged in.', 'info')
        return redirect(url_for('factor_list'))
    return render_template('auth.html', submit="login")

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('index'))

# API routes
@app.route('/factors/create', methods=['POST'])
def factor_create():
    username = request.form['username']
    ua_platform = platform(request.user_agent.string)

    public_key, status_code = create_factor(username, ua_platform)
    if status_code == 201:
        session['username'] = username
        return jsonify(public_key), status_code
    else:
        return jsonify({'Error creating passkey on the server.'}), 400

@app.route('/factors/verify', methods=['POST'])
def factor_verify():
    credential = request.json
    response, status_code = verify_factor(credential)

    if response.get('status') == 'verified':
        session['logged_in'] = True

    return jsonify(response), status_code

@app.route('/challenges/create', methods=['POST'])
def challenge_create():
    username = request.form.get('username')
    public_key, status_code = create_challenge(identity=username)
    if status_code == 201:
        return jsonify(public_key), 201
    else:
        return jsonify({'message': 'Error creating authentication challenge on the server.'}), 400

@app.route('/challenges/verify', methods=['POST'])
def challenge_verify():
    credential = request.json
    response, status_code = verify_challenge(credential)

    if response.get('status') == 'approved':
        session['logged_in'] = True
        session['username'] = response.get('entity_identity')
        
    return jsonify(response), status_code

@app.route('/factors/<sid>', methods=['DELETE'])
def factor_delete(sid):
    delete_factor(sid)
    return redirect(url_for('factor_list'))