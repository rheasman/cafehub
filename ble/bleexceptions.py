class BLEException(Exception):
    pass


class BLEOpException(BLEException):
    pass


class BLEOperationNotIssued(BLEOpException):
    EID = 1
    pass


class BLEOperationTimedOut(BLEOpException):
    EID = 2
    pass


class BLEScanException(BLEException):
    EID = 3
    pass


class BLEAlreadyScanning(BLEScanException):
    EID = 4
    pass


class BLECouldntDiscoverServices(BLEException):
    EID = 5
    pass


class BLEConnectionError(BLEException):
    EID = 6
    pass
