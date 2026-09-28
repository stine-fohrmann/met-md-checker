class MDError():
    def __init__(self, attr, message=None, severity='Error'):
        self.message = message
        self.attr = attr
        self.type = severity
        self.load()
    
    def load(self):
        pass
    
    def printFull(self, INDENT=''):
        print(INDENT + f'[{self.type}]: {self.attr} {self.message}')

class MDWarning(MDError):
    def load(self):
        self.type = 'Warning'