import functools

def callbackfn(result):
  print("callbackfn called with", result)

def cbconverter(cb):
  print("Converted", cb)
  return cb

def thread_with_callback(converter):
  def decorator(method):
    
    @functools.wraps(method)
    def methodwrap(*args, **kwargs):
      callback = kwargs["callback"]
      cc = converter(callback)
      del kwargs["callback"]
      print("callback", callback)
      print("Wrapped", method, "in", callback)
      result = method(*args, **kwargs)
      cc(result)
    
    return methodwrap

  return decorator


class TestClass:
  @thread_with_callback(cbconverter)
  def charWrite(self, uuid, data):
    """ A test charWrite thing"""
    print("charWrite", uuid, data)
    return "abc"

def t(*args, **kwargs):
  T = TestClass()
  T.charWrite(*args, **kwargs, callback=callbackfn)
  print("Name: ", T.charWrite.__name__)
  print("Doc:  ", T.charWrite.__doc__)

if __name__=="__main__":
  t(1,2)
