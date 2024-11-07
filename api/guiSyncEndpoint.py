from flask import request 
from flask_restful import Resource
import json

# Class defining the API endpoint for syncing with the Nexus GUI
class GUISyncEndpoint(Resource):
    def __init__(self, **kwargs):
        self.userSessions = kwargs["userSessions"]

    def post(self):
        content = request.get_json(force = True)
        commandList = content["command"]
        responseString = f"Command not processed: {commandList}"
        print(f"GUI POSTED: command = {commandList}")

        if (commandList[0] == "hello"):
            response = [{"a":"WHAT"}]
            return json.dumps(response), 200
        
        elif (commandList[0] == "userInfo"):
            responseString = ""
            for userSession in list(self.userSessions.userSessions.values()):
                if (userSession.isActive):
                    responseString += f"User: {userSession.userId} | "
                    for sessionObject in list(userSession.sessionObjects.values()):
                        responseString += f"{sessionObject.objectId} {(sessionObject.lastUpdateTime - sessionObject.startTime):0.2f}s {float(sessionObject.x):0.2f} {float(sessionObject.y):0.2f} {float(sessionObject.z):0.2f} | "
            if (responseString == ""):
                responseString += "No active user sessions"
            # print(responseString)
            return json.dumps(responseString), 200

        # If we get here, there is an error.
        return json.dumps(responseString), 500  

