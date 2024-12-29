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

        # TO DO: Handle multiple objects in telemetry update
        if (commandList[1] == "objectTelemetry"): 
            # print(f'TELEMETRY: {commandList}')
            counter = 2
            while (counter < len(commandList)):
                objectId = commandList[counter]
                if (self.isLogging):
                    row = [self.sessionId, self.sessionConfig["sessionName"],
                        objectId, self.lastUpdateTime]
                    row.extend(commandList[counter + 1 : counter + 7])
                    self.telemetryCsvWriter.writerow(row)
                if (objectId not in self.sessionObjects):
                    self.sessionObjects[objectId] = SessionObject(objectId)
                self.sessionObjects[objectId].lastUpdateTime = time.time()
                self.sessionObjects[objectId].pos = commandList[counter + 1 : counter + 4]
                self.sessionObjects[objectId].dir = commandList[counter + 4 : counter + 7]
                counter += 7

        # elif (commandList[1] == "config"): 
        #     self.sessionConfigDirty = True

    def closeUserSession(self):
        self.isActive = False
        self.stopLogging()

    def startLogging(self):
        if (not self.isLogging):
            if (self.telemetryCsvFile is None):
                filename = f"sessions/{time.strftime('%Y%m%d-%H%M%S')}_{self.sessionId}.csv"
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
        self.pos = [0, 0, 0]
        self.dir = [0, 0, 0]
        self.startTime = time.time()
        self.lastUpdateTime = time.time()
        self.isActive = True
        self.telemetryCsvFile = None
        self.telemetryCsvWriter = None
        self.latestTelemetryString = ""