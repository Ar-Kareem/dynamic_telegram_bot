from src.utils.affiliates import BaseAction


# This action will be called once when the main loop finished dynamically initting all scripts
class InitScriptsFinished(BaseAction): pass
# This action will be called once when the program should terminate (No further actions will be handled)
class Terminate(BaseAction):
    def __init__(self, reset_flag=False):
        super().__init__()
        self.reset_flag = reset_flag

# TELEGRAM ACTIONS

# This action will be called once when a telegram bot is initialized
class TelegramBotInitiated(BaseAction): pass
class SendTelegramMessage(BaseAction):
    def __init__(self, message: str, to: str):
        super(SendTelegramMessage, self).__init__()
        self.message = message
        self.to = to
class TelegramMessageToMe(SendTelegramMessage):
    def __init__(self, message: str):
        super(TelegramMessageToMe, self).__init__(message, to='ME')
