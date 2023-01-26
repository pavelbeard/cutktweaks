

class EmptyDirectory(Exception):
    def __init__(self, message):
        self.message = message


class EmptyDateTime(Exception):
    def __init__(self, message):
        self.message = message


class ForbiddenExtention(Exception):
    def __init__(self, message):
        self.message = message
