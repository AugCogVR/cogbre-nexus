import time
import csv

# Class for managing all user sessions
class UserSessions:
    def __init__(self):
        self.userSessions = {}

    def addUserSession(self, userId):
        self.userSessions[userId] = UserSession(userId)

    def getUserSession(self, userId):
        return self.userSessions[userId]

    def closeUserSession(self, userId):
        self.userSessions[userId].closeUserSession()
        # del self.userSessions[userId]

    def backgroundActivityCheck(self):
        inactivityThreshold = 5 # TO DO: fix arbitrary hard-coded value
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
        self.headpos = []

    def updateUserSession(self, commandList):
        # print(f"updateUserSession: {self.userId} {commandList}")
        self.lastUpdateTime = time.time()
        if (commandList[1] == "headpos"):            
            self.headpos.append([self.lastUpdateTime, commandList[2], commandList[3], commandList[4]])

    def closeUserSession(self):
        self.isActive = False
        self.saveActivity()

    def saveActivity(self):
        print(f"Saving activity for user {self.userId}")    
        filename = f"sessions/{self.userId}_{time.strftime('%Y%m%d-%H%M%S')}_head.csv"
        with open(filename, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["time", "x", "y", "z"])
            csvwriter.writerows(self.headpos)


