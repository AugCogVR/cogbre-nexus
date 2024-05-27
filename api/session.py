import time

# Class for managing all user sessions
class UserSessions:
    def __init__(self):
        self.userSessions = {}

    def addUserSession(self, userId):
        self.userSessions[userId] = UserSession(userId)

    def closeUserSession(self, userId):
        self.userSessions[userId].isActive = False
        self.userSessions[userId].saveActivity()
        # del self.userSessions[userId]

    def updateUserSession(self, userId, commandList):
        # print(f"updateUserSession: {userId} {commandList}")
        self.userSessions[userId].lastUpdateTime = time.time()

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
    
    def saveActivity(self):
        print(f"Saving activity for user {self.userId}")    

