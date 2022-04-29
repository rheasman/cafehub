"""
This type stub file was generated by pyright.
"""

'''
signatures.py
=============

A '''
__version__ = ...
class _JavaSignaturePrimitive:
    _spec = ...


jboolean = ...
jbyte = ...
jchar = ...
jdouble = ...
jfloat = ...
jint = ...
jlong = ...
jshort = ...
jvoid = ...
def JArray(of_type): # -> Type[__Primitive]:
    ''' Signature helper for identifyin'''
    ...

def with_signature(returns, takes):
    ''' Alternative version of @java_me'''
    ...

def signature(returns, takes):
    ''' Produces a JNI method signature'''
    ...
