class ServiceExceptions(Exception):
    class KduNotFound(Exception):
        def __init__(self):
            self.code = 'NOT FOUND'
            self.detail = 'KDU not found inside VNFD'
            self.status = 1
