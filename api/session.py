class SessionControllers:
    def __init__(self):
        self.sessionControllers = {}

    def addSessionController(self, sessionController):
        self.sessionControllers[sessionController.userId] = sessionController


class SessionController:
    def __init__(self, userId):
        self.userId = userId

