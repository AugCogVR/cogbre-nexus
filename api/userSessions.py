import time
import csv

# Class for managing all user sessions
class UserSessions:
    def __init__(self):
        self.userSessions = {}

    def openUserSession(self, userId):
        if (userId in self.userSessions) and (self.userSessions[userId].isActive):
            print(f"FOUND STALE SESSION for user {userId}")
            self.closeUserSession(userId)
        print(f"OPEN SESSION for user {userId}")
        self.userSessions[userId] = UserSession(userId)

    def getUserSession(self, userId):
        return self.userSessions[userId]

    def closeUserSession(self, userId):
        print(f"CLOSE SESSION for user {userId}")
        self.userSessions[userId].closeUserSession()
        # del self.userSessions[userId]  # deleting causes concurrency problemns

    def backgroundActivityCheck(self):
        inactivityThreshold = 10 # TO DO: fix arbitrary hard-coded value
        while True:
            for userId, userSession in self.userSessions.items():
                if (userSession.isActive and ((time.time() - userSession.lastUpdateTime) > inactivityThreshold)):
                    print(f"SESSION TIMEOUT for user {userId}")
                    self.closeUserSession(userId)
            time.sleep(1)

# Class for managing the data for a user session
class UserSession:
    def __init__(self, userId):
        self.userId = userId
        self.userName = "default"
        self.startTime = time.time()
        self.lastUpdateTime = time.time()
        self.isActive = True
        self.telemetryCsvFile = None
        self.telemetryCsvWriter = None
        self.sessionObjects = {}
        self.sessionConfig = {}
        self.sessionConfigDirty = False

    def updateUserSession(self, commandList):
        # print(f"updateUserSession: {self.userId} {commandList}")
        if (self.telemetryCsvFile is None):
            filename = f"sessions/{self.userId}_{time.strftime('%Y%m%d-%H%M%S')}.csv"
            self.telemetryCsvFile = open(filename, 'w')
            self.telemetryCsvWriter = csv.writer(self.telemetryCsvFile)
            self.telemetryCsvWriter.writerow(["userId", "userName", "object", "time", "x", "y", "z", "rotx", "roty", "rotz"])
        self.lastUpdateTime = time.time()
        if (commandList[1] == "object"): 
            objectId = commandList[2]
            self.telemetryCsvWriter.writerow([self.userId, self.userName, objectId, self.lastUpdateTime, commandList[3], commandList[4], commandList[5], 0, 0, 0])
            if (objectId not in self.sessionObjects):
                self.sessionObjects[objectId] = SessionObject(objectId)
            self.sessionObjects[objectId].lastUpdateTime = time.time()
            self.sessionObjects[objectId].x = commandList[3]
            self.sessionObjects[objectId].y = commandList[4]
            self.sessionObjects[objectId].z = commandList[5]
        elif (commandList[1] == "config"): 
            self.sessionConfigDirty = True
            


    def closeUserSession(self):
        self.isActive = False
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