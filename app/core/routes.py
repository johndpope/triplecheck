import os
import json
from flask import jsonify, request, make_response, send_from_directory, url_for, Response
from app import app, mongo
import logger
from werkzeug.utils import secure_filename
import datetime
import maya
from twisted.logger import globalLogPublisher
from umbral.keys import UmbralPublicKey
import hashlib

from nucypher.characters.lawful import Alice, Bob, Ursula
from nucypher.characters.lawful import Enrico as Enrico
from nucypher.network.middleware import RestMiddleware
from nucypher.utilities.logging import SimpleObserver

SEEDNODE_URI = "https://localhost:11501"

ROOT_PATH = os.environ.get('ROOT_PATH')
LOG = logger.get_root_logger(__name__, filename=os.path.join(ROOT_PATH, 'output.log'))

UPLOAD_FOLDER = '/Users/Harish1/Desktop/work/ethnyc/triplecheck/uploads'
ENCRYPTED_FOLDER = '/Users/Harish1/Desktop/work/ethnyc/triplecheck/encrypted'
ALLOWED_EXTENSIONS = set(['txt', 'jpg', 'jpeg'])

# Connect to Ursula
ursula = Ursula.from_seed_and_stake_info(seed_uri=SEEDNODE_URI,federated_only=True,minimum_stake=0)

#Define Demo Charaters
ALICE = Alice(network_middleware=RestMiddleware(),known_nodes=[ursula],learn_on_same_thread=True,federated_only=True)
BOB = Bob(known_nodes=[ursula],network_middleware=RestMiddleware(),federated_only=True,start_learning_now=True,learn_on_same_thread=True)

def sha256sum(filename):
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()

def decrypt(enchash, passlabel):
    data = mongo.db.encrypted.find_one({"hash": enchash})
    pubkey, posterstamp = getPolicyKey(data['policy'])
    decryptedfulltext = ""
    if data is not None:
        with open((os.path.join(app.config['UPLOAD_FOLDER'], data['name'])), 'rb') as file:
            cleartext = file.readlines()
            for counter, plaintext in enumerate(cleartext):
                enrico = Enrico(policy_encrypting_key=pubkey)
                single_passage_ciphertext, _signature = enrico.encrypt_message(plaintext)
                data_source_public_key = bytes(enrico.stamp)
                enrico_as_understood_by_bob = Enrico.from_public_keys(verifying_key=data_source_public_key,policy_encrypting_key=pubkey)
                alicepubkey = UmbralPublicKey.from_bytes(posterstamp)
                delivered_cleartexts = BOB.retrieve(message_kit=single_passage_ciphertext,data_source=enrico_as_understood_by_bob,alice_verifying_key=alicepubkey,label=bytes(passlabel))
                decryptedfulltext.append(delivered_cleartexts)
        return decryptedfulltext
    else:
        return make_response(jsonify({'error': 'data not found'}), 404)

def getPolicyKey(n):
    if n == 1:
        #policy1
        policy1pass = b'ethnewyork'
        policy1_pubkey = ALICE.get_policy_pubkey_from_label(policy1pass)
        policyexpiry =  maya.now() + datetime.timedelta(days=5)
        activepolicy = ALICE.grant(BOB, policy1pass, m=2, n=3, expiration=policyexpiry)
        ap1 = bytes(ALICE.stamp)
        if activepolicy.public_key == policy1_pubkey:
            print("key 1 is created and in scope")
        return policy1_pubkey, ap1
    if n == 2:
        #policy2
        policy2pass = b'ethglobal'
        policy2_pubkey = ALICE.get_policy_pubkey_from_label(policy2pass)
        policyexpiry =  maya.now() + datetime.timedelta(days=5)
        activepolicy = ALICE.grant(BOB, policy2pass, m=2, n=3, expiration=policyexpiry)
        ap2 = bytes(ALICE.stamp)
        if activepolicy.public_key == policy2_pubkey:
            print("key 2 is created and in scope")
        return policy2_pubkey, ap2


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if request.form['policy'] == "policy1":
            setpolicy = 1
        if request.form['policy'] == "policy2":
            setpolicy = 2
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

            '''
            #encrypt to provided policy
            encryptedByteArray = encrypt(setpolicy,file)
            encfile = open(os.path.join(ENCRYPTED_FOLDER, filename), 'w+b')
            encfile.write(encryptedByteArray)
            encfile.close()
            '''
            filehash = sha256sum(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            fileurl = "/decrypt?hash=" + filehash
            stordata = { "name" : filename, "hash": filehash ,"policy": setpolicy, "url" : fileurl}
            mongo.db.encrypted.insert_one(stordata)
            return Response(json.dumps({'success':True}),  mimetype='application/json')    #Change response to 200 OK
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <select name="policy">
          <option value="policy1">Policy 1</option>
          <option value="policy2">Policy 2</option>
      </select>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt_file():
    if request.method == 'POST':
        filehash = request.form['hash']
        filelabel = request.form['pass']
        decrypted_data = decrypt(filehash, filelabel)
        return decrypted_data
    return '''
    <!doctype html>
    <title>decrypt file</title>
    <h1>decrypt</h1>
    <form method=post enctype=multipart/form-data>
      <input type=text name=hash>
      <input type=text name=pass>
      <input type=submit value=decrypt>
    </form>
    '''







