import logging
import traceback

from oscpy.client import OSCClient

class MsgHandler(logging.Handler):
    def __init__(self, oscclient: OSCClient, level : int = logging.NOTSET):
        super().__init__(level)
        self.Client = oscclient

    def emit(self, record : logging.LogRecord) -> None:
        log_entry = self.format(record)
        try:
            pass
            # self.Client.send_message(b"/message", [log_entry])
        except:
            tb = traceback.format_exc()
            print(tb)

        
