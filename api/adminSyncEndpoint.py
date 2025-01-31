from flask import request 
from flask_restful import Resource
import json

# Class defining the API endpoint for the Nexus GUI frontend, which
# can be used to monitor and configure a Nexus user session.
class AdminSyncEndpoint(Resource):
    def __init__(self, **kwargs):
        self.userSessions = kwargs["userSessions"]

    def post(self):
        content = request.get_json(force = True)
        commandList = content["command"]
        responseString = f"Command not processed: {commandList}"

        # Report the command received, unless it's a very frequent activity update
        if (commandList[0] == "get_telemetry"):
            print("!", end="")
        else:
            print(f"ADMIN POSTED: command = {content['command']}")

        # Return the active users 
        if (commandList[0] == "get_active_user_list"):
            responseObject = []
            for userSession in list(self.userSessions.userSessions.values()):
                if (userSession.isActive):
                    responseObject.append({"id" : userSession.sessionId, "name" : userSession.sessionConfig["general|session_name"]})
            return json.dumps(responseObject), 200

        # Return current version of the config
        elif (commandList[0] == "get_config"):
            sessionId = commandList[1]
            responseObject = {}
            if (sessionId in self.userSessions.userSessions):
                userSession = self.userSessions.getUserSession(sessionId)
                if (userSession.isActive):
                    responseObject = userSession.sessionConfig
            return json.dumps(responseObject), 200

        # Set a new config 
        elif (commandList[0] == "set_config"):
            sessionId = commandList[1]
            newConfigJson = commandList[2]
            # print("GOT NEW CONFIG: ", newConfigJson)
            if (sessionId in self.userSessions.userSessions):
                userSession = self.userSessions.getUserSession(sessionId)
                if (userSession.isActive):
                    userSession.sessionConfig = json.loads(newConfigJson)
                    userSession.sessionConfigDirty = True
            responseObject = {}
            return json.dumps(responseObject), 200

       # Start logging
        elif (commandList[0] == "start_logging"):
            # print("START LOGGING " + commandList[1])
            sessionId = commandList[1]
            userSession = self.userSessions.getUserSession(sessionId)
            if ((userSession is not None) and (userSession.isActive)):
                userSession.startLogging()
            responseObject = {}
            return json.dumps(responseObject), 200
 
       # Stop logging
        elif (commandList[0] == "stop_logging"):
            # print("STOP LOGGING " + commandList[1])
            sessionId = commandList[1]
            userSession = self.userSessions.getUserSession(sessionId)
            if ((userSession is not None) and (userSession.isActive)):
                userSession.stopTelemetryLogging()
                userSession.stopEventLogging()
            responseObject = {}
            return json.dumps(responseObject), 200
        
        # Return user and object telemetry
        elif (commandList[0] == "get_telemetry"):
            sessionId = commandList[1]
            responseObject = []
            if (sessionId in self.userSessions.userSessions):
                userSession = self.userSessions.getUserSession(sessionId)
                if (userSession.isActive):
                    for sessionObject in list(userSession.sessionObjects.values()):
                        responseObject.append({"id":sessionObject.objectId, 
                                               "time":f"{(sessionObject.lastUpdateTime - sessionObject.startTime):0.2f}s", 
                                               "x":f"{float(sessionObject.pos[0]):0.2f}",
                                               "y":f"{float(sessionObject.pos[1]):0.2f}",
                                               "z":f"{float(sessionObject.pos[2]):0.2f}"})
            return json.dumps(responseObject), 200

        # If we get here, there is an error.
        return json.dumps(responseString), 500  

