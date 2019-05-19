#!/usr/bin/env python
import os
import json
from flask import Flask, flash, request, redirect, url_for, Response, jsonify
from werkzeug.utils import secure_filename
from flask import send_from_directory

## NuCypher Imports
import datetime
import maya
from twisted.logger import globalLogPublisher
from umbral.keys import UmbralPublicKey

from nucypher.characters.lawful import Alice, Bob, Ursula
from nucypher.characters.lawful import Enrico as Enrico
from nucypher.network.middleware import RestMiddleware
from nucypher.utilities.logging import SimpleObserver

######################################
# Triplecheck & NuCypher setup stuff #
######################################

SEEDNODE_URI = "https://localhost:11501"

# Twisted Logger
globalLogPublisher.addObserver(SimpleObserver())

# Flask Upload & allowed extensions config
UPLOAD_FOLDER = '/home/ubuntu/triplecheck/uploads'
ENCRYPTED_FOLDER = '/home/ubuntu/triplecheck/encrypted'
ALLOWED_EXTENSIONS = set(['txt', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Connect to Ursula
ursula = Ursula.from_seed_and_stake_info(seed_uri=SEEDNODE_URI,federated_only=True,minimum_stake=0)

#Define Demo Charaters
ALICE = Alice(network_middleware=RestMiddleware(),known_nodes=[ursula],learn_on_same_thread=True,federated_only=True)
BOB = Bob(known_nodes=[ursula],network_middleware=RestMiddleware(),federated_only=True,start_learning_now=True,learn_on_same_thread=True)


policy_pubkey = ALICE.get_policy_pubkey_from_label(label)

ALICE.start_learning_loop(now=True)

policy = ALICE.grant(BOB,label,m=m, n=n,expiration=policy_end_datetime)

privatelyshared = bytes(ALICE.stamp)

BOB.join_policy(label, privatelyshared)

enrico = Enrico(policy_encrypting_key=policy_pubkey)

def encrypt(setpolicy, f):
    enrico = Enrico(policy_encrypting_key=getPolicyKey(setpolicy))
    payload = f.readlines()
    ciphertext, _signature = enrico.encrypt_message(payload)
    return ciphertext

def decrypt():
    return

def grantAccess(party, selpolicy):
    return ALICE.grant(party,selpolicy.label,m=selpolicy.m, n=selpolicy.n,expiration=selpolicy.policy_end_datetime)

def getPublicKey(policyname):
    return ALICE.get_policy_pubkey_from_label(label)

def create_policy(pname,passtxt,expirydays):
    newpolicy["policy_end_datetime"] = maya.now() + datetime.timedelta(days=expirydays)
    newpolicy["m"] = 2
    newpolicy["n"] = 3
    newpolicy["label"] = b(passtxt)
    newpolicy["name"] = pname
    return newpolicy

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return "Welcome to nucypher publishing server - index"

#Explorer + Home
@app.route('/listEncryptedFiles')   #ID, Filename, Hash, Expiration, URL
@app.route('/listPublicFiles')       #ID, IPFS Proxy Link, Public Key

@app.route('/verify') #Public Key
@app.route('/decrypt') #hash, password

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            jsresp = [ { "name" : filename, "url" : url_for('uploaded_file', filename=filename)} ]
            return Response(json.dumps(jsresp),  mimetype='application/json')    #Change response to 200 OK
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/listPolicies')
@app.route('/policy', methods=['GET', 'POST'])
def addpolicy():
    # policyName, policyExpirationDate, policyPassword
    return

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')

