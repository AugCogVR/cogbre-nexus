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
        self.lastUpdateTime = time.time()
        self.isActive = True
        self.telemetryCsvFile = None
        self.telemetryCsvWriter = None
        self.latestTelemetryString = ""

    def updateUserSession(self, commandList):
        # print(f"updateUserSession: {self.userId} {commandList}")
        if (self.telemetryCsvFile is None):
            filename = f"sessions/{self.userId}_{time.strftime('%Y%m%d-%H%M%S')}.csv"
            self.telemetryCsvFile = open(filename, 'w')
            self.telemetryCsvWriter = csv.writer(self.telemetryCsvFile)
            self.telemetryCsvWriter.writerow(["object", "time", "x", "y", "z"])
        self.lastUpdateTime = time.time()
        self.latestTelemetryString = f"{commandList[1]} {self.lastUpdateTime} {commandList[2]} {commandList[3]} {commandList[4]}"
        if (commandList[1] == "headpos"):
            self.telemetryCsvWriter.writerow(["headpos", self.lastUpdateTime, commandList[2], commandList[3], commandList[4]])

    def closeUserSession(self):
        self.isActive = False
        if (self.telemetryCsvFile is not None):
            self.telemetryCsvFile.close()
            self.telemetryCsvFile = None
            self.telemetryCsvWriter = None

