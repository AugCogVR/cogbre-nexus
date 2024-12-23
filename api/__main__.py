from flask import Flask, request #, jsonify, render_template 
from flask_restful import Resource, Api #, reqparse
import random
import string
import json
import os
import sys
import argparse
import shlex
import time
import threading
import logging
from userSessions import *
from clientSyncEndpoint import *
from adminSyncEndpoint import *

# Parse command line args
parser = argparse.ArgumentParser('cogbre nexus API server')
parser.add_argument("--oxidepath", type=str, help="Path to active Oxide installation.", required=False, default="../oxide/")
parser.add_argument("--caparulespath", type=str, help="Path to Capa rules files.", required=False, default="../oxide/datasets/capa-rules/")
args = parser.parse_args()
print(f'oxide path: {args.oxidepath}')
print(f'capa rules path: {args.caparulespath}')

# Import Oxide 
sys.path.append(args.oxidepath+'/src')
sys.path.append(args.oxidepath+'/src/oxide')
from oxide.core import oxide as local_oxide
# local_oxide.logger.setLevel(logging.DEBUG)

# Set Flask/werkzeug log level
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Create set of client session contollers
userSessions = UserSessions()

# Set up thread to check for lack of client user activity 
backgroundThread = threading.Thread(target=userSessions.backgroundActivityCheck)
backgroundThread.start()

# Set up web app
app = Flask(__name__)

# Set up API
api = Api(app)

# Set up the primary endpoint for the VR clients
# (not following API best practices of one resource/entry point per function)
api.add_resource(ClientSyncEndpoint, "/client_sync",
                 resource_class_kwargs={"userSessions":userSessions, 
                                        "local_oxide":local_oxide,
                                        "capaRulesPath":args.caparulespath})  

# Set up the primary endpoint for the Nexus Admin GUI
api.add_resource(AdminSyncEndpoint, "/admin_sync",
                 resource_class_kwargs={"userSessions":userSessions})

# Run the Flask app
if __name__ == "__main__":
    app.run() 


