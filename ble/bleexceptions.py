class BLEException(Exception):
  pass

class BLEOpException(BLEException):
  pass

class BLEOperationNotIssued(BLEOpException):
  pass

class BLEOperationTimedOut(BLEOpException):
  pass

class BLEScanException(BLEException):
  pass

class BLEAlreadyScanning(BLEScanException):
  pass

class BLECouldntDiscoverServices(BLEException):
  pass

