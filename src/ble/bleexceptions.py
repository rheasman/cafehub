# Note that 1000 will be used for exceptions with no known type
class UnknownException(Exception):
    EID = 1000

class BLEException(Exception):
    EID = 20000

class BLEOpException(BLEException):
    EID = 500

class BLEOperationNotIssued(BLEOpException):
    EID = 1

class BLEOperationTimedOut(BLEOpException):
    EID = 2

class BLEScanException(BLEException):
    EID = 3

class BLEAlreadyScanning(BLEScanException):
    EID = 4

class BLECouldntDiscoverServices(BLEException):
    EID = 5

class BLEConnectionError(BLEException):
    EID = 6

class BLEMismatchedOperation(BLEException):
    EID = 7

class BLENoCallbackProvided(BLEException):
    EID = 8
