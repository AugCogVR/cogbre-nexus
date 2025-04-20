import time
import csv
import base64
import threading

# Create locks to synchronize log writing
eventLogLock = threading.Lock()
telemetryLogLock = threading.Lock()

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
        if (sessionId in self.userSessions):
            print(f"CLOSE SESSION {sessionId}")
            self.userSessions[sessionId].closeUserSession()
            # del self.userSessions[sessionId]  # deleting causes concurrency problemns

    # Check for inactive users and close their sessions if inactivity 
    # exceeds the threshold established for this user.
    # This method is called by the backgroundThread established in __main.py__.
    def backgroundActivityCheck(self):
        while True:
            for sessionId, userSession in self.userSessions.items():
                if (userSession.isActive and ((time.time() - userSession.lastUpdateTime) > userSession.inactivityThreshold)):
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
        self.isEventLogging = False
        self.eventCsvFile = None
        self.eventCsvWriter = None
        self.isTelemetryLogging = False
        self.telemetryCsvFile = None
        self.telemetryCsvWriter = None
        self.sessionObjects = {}
        self.sessionConfig = {}
        self.sessionConfigDirty = False
        self.inactivityThreshold = 10
        self.aiPayloadQueue = []
        self.aiPayloadQueueLock = threading.Lock()

    def updateUserSession(self, commandList):
        # print(f"updateUserSession: {self.sessionId} {commandList}")
        self.lastUpdateTime = time.time()

        # Process an event (create / update / destroy object, etc.)
        # except for telemetry (position/orientation) -- see below.
        if (commandList[1] == "event"): 
            # print(f'EVENT: {commandList}')
            counter = 2
            action = commandList[counter]
            # print(f"ACTION: {action}")
            counter += 1
            objectId = commandList[counter]
            # print(f"OBJECTID: {objectId}")
            if (action == "create"):
                counter += 1
                objectName = commandList[counter]
                # print(f"OBJECTNAME: {objectName}")
                counter += 1
                details = commandList[counter]
                # print(f"DETAILS: {details}")
                # # https://www.geeksforgeeks.org/encoding-and-decoding-base64-strings-in-python/
                # detailsB64 = base64.b64decode(details.encode("ascii")).decode("ascii")
                # print(f"B64 decoded details: {detailsB64}")
                counter += 1
                if (self.isEventLogging):
                    row = [self.sessionId, # self.sessionConfig["general|session_name"],
                        action, objectId, objectName, self.lastUpdateTime, details]
                    self.eventCsvWriter.writerow(row)
                if (objectId not in self.sessionObjects):
                    self.sessionObjects[objectId] = SessionObject(objectId)
                    self.sessionObjects[objectId].startTime = time.time()
            if (action == "update"):
                counter += 1
                details = commandList[counter]
                if (self.isEventLogging):
                    row = [self.sessionId, # self.sessionConfig["general|session_name"],
                        action, objectId, '', self.lastUpdateTime, details]
                    with eventLogLock:
                        self.eventCsvWriter.writerow(row)
            if (action == "destroy"):
                if (self.isEventLogging):
                    row = [self.sessionId, # self.sessionConfig["general|session_name"],
                        action, objectId, '', self.lastUpdateTime, '']
                    with eventLogLock:
                        self.eventCsvWriter.writerow(row)
                if (objectId in self.sessionObjects):
                    del self.sessionObjects[objectId] 
            if (action == "question_select"):
                if (self.isEventLogging):
                    # abuse "objectId" as the question ID
                    row = [self.sessionId, # self.sessionConfig["general|session_name"],
                        action, objectId, '', self.lastUpdateTime, '']
                    with eventLogLock:
                        self.eventCsvWriter.writerow(row)

        # Process telemetry (object position and orientation). 
        # Handle multiple objects in single telemetry update.
        if (commandList[1] == "objectTelemetry"): 
            # print(f'TELEMETRY: {commandList}')
            counter = 2
            while (counter < len(commandList)):
                objectId = commandList[counter]
                counter += 1
                objectName = commandList[counter]
                if (self.isTelemetryLogging):
                    row = [self.sessionId, # self.sessionConfig["general|session_name"],
                        objectId, objectName, self.lastUpdateTime]
                    row.extend(commandList[counter + 1 : counter + 7])
                    with telemetryLogLock:
                        self.telemetryCsvWriter.writerow(row)
                if (objectId not in self.sessionObjects):
                    self.sessionObjects[objectId] = SessionObject(objectId)
                self.sessionObjects[objectId].lastUpdateTime = time.time()
                self.sessionObjects[objectId].pos = commandList[counter + 1 : counter + 4]
                self.sessionObjects[objectId].dir = commandList[counter + 4 : counter + 7]
                counter += 7

    def closeUserSession(self):
        self.isActive = False
        self.stopEventLogging()
        self.stopTelemetryLogging()

    def startEventLogging(self):
        if (not self.isEventLogging):
            if (self.eventCsvFile is None):
                filename = f"sessions/{time.strftime('%Y%m%d-%H%M%S')}_{self.sessionId}_events.csv"
                self.eventCsvFile = open(filename, 'w')
                self.eventCsvWriter = csv.writer(self.eventCsvFile)
                self.eventCsvWriter.writerow(["sessionId", "action", "objectId", "objectName", "time", "details"])
            self.loggingStartTime = time.time()
            self.isEventLogging = True

    def stopEventLogging(self):
        if (self.isEventLogging):
            self.isEventLogging = False
            if (self.eventCsvFile is not None):
                self.eventCsvFile.close()
                self.eventCsvFile = None
                self.eventCsvWriter = None
                
    def startTelemetryLogging(self):
        if (not self.isTelemetryLogging):
            if (self.telemetryCsvFile is None):
                filename = f"sessions/{time.strftime('%Y%m%d-%H%M%S')}_{self.sessionId}_telemetry.csv"
                self.telemetryCsvFile = open(filename, 'w')
                self.telemetryCsvWriter = csv.writer(self.telemetryCsvFile)
                self.telemetryCsvWriter.writerow(["sessionId", "objectId", "objectName", "time", "x", "y", "z", "rotx", "roty", "rotz"])
            self.loggingStartTime = time.time()
            self.isTelemetryLogging = True

    def stopTelemetryLogging(self):
        if (self.isTelemetryLogging):
            self.isTelemetryLogging = False
            if (self.telemetryCsvFile is not None):
                self.telemetryCsvFile.close()
                self.telemetryCsvFile = None
                self.telemetryCsvWriter = None

    def pushAIPayload(self, payload):
        with self.aiPayloadQueueLock:
            print(f"For sessionId {self.sessionId} push AI payload: {payload}")
            self.aiPayloadQueue.append(payload)

    def popAIPayload(self):
        with self.aiPayloadQueueLock:
            if (self.aiPayloadQueue):
                return(self.aiPayloadQueue.pop(0))
            else:
                return None
        
class SessionObject:
    def __init__(self, objectId):
        self.objectId = objectId
        self.pos = [0, 0, 0]
        self.dir = [0, 0, 0]
        self.startTime = time.time()
        self.lastUpdateTime = time.time()
        # self.isActive = True
        # self.eventCsvFile = None
        # self.eventCsvWriter = None
        # self.telemetryCsvFile = None
        # self.telemetryCsvWriter = None
        # self.latestTelemetryString = ""