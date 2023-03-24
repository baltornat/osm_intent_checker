class ApiExceptions(Exception):
    class CnfPackageUploadException(Exception):
        def __init__(self, code, detail, status):
            self.code = code
            self.detail = detail
            self.status = status

    class NsPackageUploadException(Exception):
        def __init__(self, code, detail, status):
            self.code = code
            self.detail = detail
            self.status = status

    class DeploymentException(Exception):
        def __init__(self, code, detail, status):
            self.code = code
            self.detail = detail
            self.status = status

    class TokenExpiredException(Exception):
        def __init__(self):
            self.code = 'EXPIRED'
            self.detail = 'Token already expired'
            self.status = 1

    class VimNotFound(Exception):
        def __init__(self):
            self.code = 'NOT FOUND'
            self.detail = 'VIM account not found'
            self.status = 2

    class CannotLogout(Exception):
        def __init__(self):
            self.code = 'LOGOUT FAIL'
            self.detail = 'An error occurred during logout'
            self.status = 3
