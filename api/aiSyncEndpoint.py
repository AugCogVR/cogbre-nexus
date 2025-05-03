from flask import request 
from flask_restful import Resource
import json
import x3dConverter

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

            # TEMPORARY (???) HACK: If we have a graph, convert it to X3D and dump to file
            if False:
                payloadObject = json.loads(payloadString)
                if payloadObject["payload_type"] == "graph":
                    print(f"\n\n\n*** TRY TO CONVERT {payloadObject["id"]} TO X3D!")
                    x3dString = x3dConverter.json_to_x3d(payloadObject)
                    print(f"\n\n\n*** RESULT: {x3dString}")
                    with open("graph_output.x3d", "w") as out:
                        out.write(x3dString)

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

