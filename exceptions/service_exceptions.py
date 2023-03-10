class NotSol006(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.code = 1


class PackageNotValid(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.code = 2


class KduNotFound(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.code = 3
