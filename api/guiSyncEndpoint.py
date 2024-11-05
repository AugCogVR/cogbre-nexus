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

# Class defining the API endpoint for syncing with the Nexus GUI
class GUISyncEndpoint(Resource):
    def post(self):
        content = request.get_json(force = True)
        commandList = content["command"]
        responseString = f"Command not processed: {commandList}"
        print(f"GUI POSTED: command = {commandList}")

        if (commandList[0] == "hello"):
            response = [{"a":"WHAT"}]
            return json.dumps(response), 200
        
        elif (commandList[0] == "userInfo"):
            response = [{"a":"WHAT"}]
            # htmlString = ""
            # for user in list(userSessions.userSessions.values()):
            #     if (user.isActive):
            #         htmlString += f"User: {user.userId}<p>"
            #         htmlString += user.latestTelemetryString + "<p>"
            # if (htmlString == ""):
            #     htmlString += "No active user sessions"
            # # print(htmlString)
            # return htmlString
            return json.dumps(response), 200

        # If we get here, there is an error.
        return json.dumps(responseString), 500  

