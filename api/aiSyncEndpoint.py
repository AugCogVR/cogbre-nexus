from flask import request 
from flask_restful import Resource
import json
import time

# Class defining the API endpoint for the AI Assistant.
class AISyncEndpoint(Resource):
    def __init__(self, **kwargs):
        self.userSessions = kwargs["userSessions"]

    def post(self):
        content = request.get_json(force = True)
        sessionId = content["sessionId"]
        commandList = content["command"]

        responseString = f"Command not processed: {commandList}"

        # Report the command received
        print(f"AI POSTED: sessionId = {sessionId}, command = {commandList}")

        # Push AI payload to queue in appropriate user session object 
        if (commandList[0] == "push_ai_payload"):
            payloadString = commandList[1]

            # TODO: Actually use the given session ID once we know it's being set properly
            # userSession = self.userSessions.getUserSession(sessionId)
            # Until then, just grab the first ACTIVE user session
            allUserSessions = list(self.userSessions.userSessions.values())
            for userSession in allUserSessions:
                if userSession.isActive:
                    userSession.pushAIPayload(payloadString)
                    print(f"userSession {userSession.sessionId} push AI payload {payloadString}")
                    break

            # TODO: more informative response
            return json.dumps("ok"), 200

        # If we get here, there is an error.
        return json.dumps(responseString), 500  

