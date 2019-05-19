import os
import json
import datetime
from bson.objectid import ObjectId
from flask import Flask, flash, request, redirect, url_for, Response, jsonify
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask_pymongo import PyMongo


## NuCypher Imports
import datetime
import maya
from twisted.logger import globalLogPublisher
from umbral.keys import UmbralPublicKey

from nucypher.characters.lawful import Alice, Bob, Ursula
from nucypher.characters.lawful import Enrico as Enrico
from nucypher.network.middleware import RestMiddleware
from nucypher.utilities.logging import SimpleObserver

class JSONEncoder(json.JSONEncoder):
    ''' extend json-encoder class'''

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


# Flask Upload & allowed extensions config
UPLOAD_FOLDER = '/home/ubuntu/triplecheck/uploads'
ENCRYPTED_FOLDER = '/home/ubuntu/triplecheck/encrypted'
ALLOWED_EXTENSIONS = set(['txt', 'jpg', 'jpeg'])

app = Flask(__name__)

# add mongo url to flask config, so that flask_pymongo can use it to make connection
app.config['MONGO_URI'] = os.environ.get('DB')
mongo = PyMongo(app)

# use the modified encoder class to handle ObjectId & datetime object while jsonifying the response.
app.json_encoder = JSONEncoder


######################################
# Triplecheck & NuCypher setup stuff #
######################################

SEEDNODE_URI = "https://localhost:11501"

# Twisted Logger
globalLogPublisher.addObserver(SimpleObserver())

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Connect to Ursula
ursula = Ursula.from_seed_and_stake_info(seed_uri=SEEDNODE_URI,federated_only=True,minimum_stake=0)

#Define Demo Charaters
ALICE = Alice(network_middleware=RestMiddleware(),known_nodes=[ursula],learn_on_same_thread=True,federated_only=True)
BOB = Bob(known_nodes=[ursula],network_middleware=RestMiddleware(),federated_only=True,start_learning_now=True,learn_on_same_thread=True)


from app.core import *