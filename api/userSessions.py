import time
import csv

# Class for managing all user sessions
class UserSessions:
    def __init__(self):
        self.userSessions = {}

    def openUserSession(self, sessionId):
        if (sessionId in self.userSessions) and (self.userSessions[sessionId].isActive):
            print(f"FOUND STALE SESSION {sessionId}")
            self.closeUserSession(sessionId)
        print(f"OPEN SESSION {sessionId}")
        self.userSessions[sessionId] = UserSession(sessionId)

    def getUserSession(self, sessionId):
        if (sessionId in self.userSessions):
            return self.userSessions[sessionId]
        return None

    def closeUserSession(self, sessionId):
        print(f"CLOSE SESSION {sessionId}")
        self.userSessions[sessionId].closeUserSession()
        # del self.userSessions[sessionId]  # deleting causes concurrency problemns

    def backgroundActivityCheck(self):
        inactivityThreshold = 10 # TO DO: fix arbitrary hard-coded value
        while True:
            for sessionId, userSession in self.userSessions.items():
                if (userSession.isActive and ((time.time() - userSession.lastUpdateTime) > inactivityThreshold)):
                    print(f"SESSION TIMEOUT for {sessionId}")
                    self.closeUserSession(sessionId)
            time.sleep(1)

# Class for managing the data for a user session
class UserSession:
    def __init__(self, sessionId):
        self.sessionId = sessionId
        self.loggingStartTime = time.time()
        self.lastUpdateTime = time.time()
        self.isActive = True
        self.isLogging = False
        self.telemetryCsvFile = None
        self.telemetryCsvWriter = None
        self.sessionObjects = {}
        self.sessionConfig = {}
        self.sessionConfigDirty = False

    def updateUserSession(self, commandList):
        # print(f"updateUserSession: {self.sessionId} {commandList}")
        self.lastUpdateTime = time.time()
        if (commandList[1] == "object"): 
            objectId = commandList[2]
            if (self.isLogging):
                self.telemetryCsvWriter.writerow([self.sessionId, self.sessionConfig["sessionName"], objectId, self.lastUpdateTime, commandList[3], commandList[4], commandList[5], 0, 0, 0])
            if (objectId not in self.sessionObjects):
                self.sessionObjects[objectId] = SessionObject(objectId)
            self.sessionObjects[objectId].lastUpdateTime = time.time()
            self.sessionObjects[objectId].x = commandList[3]
            self.sessionObjects[objectId].y = commandList[4]
            self.sessionObjects[objectId].z = commandList[5]
        # elif (commandList[1] == "config"): 
        #     self.sessionConfigDirty = True

    def closeUserSession(self):
        self.isActive = False
        self.stopLogging()

    def startLogging(self):
        if (not self.isLogging):
            if (self.telemetryCsvFile is None):
                filename = f"sessions/{self.sessionId}_{time.strftime('%Y%m%d-%H%M%S')}.csv"
                self.telemetryCsvFile = open(filename, 'w')
                self.telemetryCsvWriter = csv.writer(self.telemetryCsvFile)
                self.telemetryCsvWriter.writerow(["sessionId", "sessionName", "object", "time", "x", "y", "z", "rotx", "roty", "rotz"])
            self.loggingStartTime = time.time()
            self.isLogging = True

    def stopLogging(self):
        if (self.isLogging):
            self.isLogging = False
            if (self.telemetryCsvFile is not None):
                self.telemetryCsvFile.close()
                self.telemetryCsvFile = None
                self.telemetryCsvWriter = None

class SessionObject:
    def __init__(self, objectId):
        self.objectId = objectId
        self.x = 0
        self.y = 0
        self.z = 0
        self.rotx = 0
        self.roty = 0
        self.rotz = 0
        self.startTime = time.time()
        self.lastUpdateTime = time.time()
        self.isActive = True
        self.telemetryCsvFile = None
        self.telemetryCsvWriter = None
        self.latestTelemetryString = ""