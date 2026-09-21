
class Error():
    def __init__(self, attr, message=None, severity='Error'):
        self.message = message
        self.attr = attr
        self.type = severity
        self.load()
    
    def load(self):
        pass
    
    def printFull(self, INDENT=''):
        print(INDENT + f'{self.type}: {self.attr} {self.message}')

class UndefinedError(Error):
    def __init__(self, attr, message='is not defined'):
        super(UndefinedError, self).__init__(attr, message)
        self.message = message
        # self.attr = attr

class EmptyError(Error):
    def __init__(self, attr, message='is empty'):
        super(EmptyError, self).__init__(attr, message)
        self.message = message
        # self.attr = attr

class InconsistentLengthError(Error):
    def __init__(self, attrs: list, message='don\'t have the same number of elements.'):
        super(InconsistentLengthError, self).__init__(attr, message)
        self.attrs = attrs
        self.message = message
    
    def printFull(self, INDENT=''):
        print(INDENT + f'{self.type}: {", ".join([a for a in self.attrs])} {self.message}')


class MDWarning(Error):
    def load(self):
        self.type = 'Warning'

# class EmptyWarning(Warning):
#     def __init__(self, attr, message='is empty'):
#         super(EmptyWarning, self).__init__(attr, message)

# class EmptyWarning(EmptyError):
#     def __init__(self, attr, message):
#         super(EmptyWarning, self).__init__(attr, message)
#         self.type = 'Warning'