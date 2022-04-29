"""
This type stub file was generated by pyright.
"""

from six import with_metaclass
from .jnius import JavaClass, MetaJavaClass

__all__ = ('autoclass', 'ensureclass', 'protocol_map')
log = ...
class Class(with_metaclass(MetaJavaClass, JavaClass)):
    __javaclass__ = ...
    desiredAssertionStatus = ...
    forName = ...
    getClassLoader = ...
    getClasses = ...
    getComponentType = ...
    getConstructor = ...
    getConstructors = ...
    getDeclaredClasses = ...
    getDeclaredConstructor = ...
    getDeclaredConstructors = ...
    getDeclaredField = ...
    getDeclaredFields = ...
    getDeclaredMethod = ...
    getDeclaredMethods = ...
    getDeclaringClass = ...
    getField = ...
    getFields = ...
    getInterfaces = ...
    getMethod = ...
    getMethods = ...
    getModifiers = ...
    getName = ...
    getPackage = ...
    getProtectionDomain = ...
    getResource = ...
    getResourceAsStream = ...
    getSigners = ...
    getSuperclass = ...
    isArray = ...
    isAssignableFrom = ...
    isInstance = ...
    isInterface = ...
    isPrimitive = ...
    newInstance = ...
    toString = ...
    def __str__(self) -> str:
        ...
    
    def __repr__(self): # -> str:
        ...
    


class Object(with_metaclass(MetaJavaClass, JavaClass)):
    __javaclass__ = ...
    getClass = ...
    hashCode = ...


class Modifier(with_metaclass(MetaJavaClass, JavaClass)):
    __javaclass__ = ...
    isAbstract = ...
    isFinal = ...
    isInterface = ...
    isNative = ...
    isPrivate = ...
    isProtected = ...
    isPublic = ...
    isStatic = ...
    isStrict = ...
    isSynchronized = ...
    isTransient = ...
    isVolatile = ...


class Method(with_metaclass(MetaJavaClass, JavaClass)):
    __javaclass__ = ...
    getName = ...
    toString = ...
    getParameterTypes = ...
    getReturnType = ...
    getModifiers = ...
    isVarArgs = ...
    isDefault = ...


class Field(with_metaclass(MetaJavaClass, JavaClass)):
    __javaclass__ = ...
    getName = ...
    toString = ...
    getType = ...
    getModifiers = ...


class Constructor(with_metaclass(MetaJavaClass, JavaClass)):
    __javaclass__ = ...
    toString = ...
    getParameterTypes = ...
    getModifiers = ...
    isVarArgs = ...


registers = ...
def ensureclass(clsname): # -> None:
    ...

def lower_name(s): # -> Literal['']:
    ...

def bean_getter(s): # -> Literal[False]:
    ...

def log_method(method, name, signature): # -> None:
    ...

def identify_hierarchy(cls, level, concrete=...): # -> Generator[tuple[Unknown, Unknown], None, None]:
    ...

def autoclass(clsname, include_protected=..., include_private=...):
    ...

class Py2Iterator:
    '''
    In py2 the next() is called'''
    def __init__(self, java_iterator) -> None:
        ...
    
    def __iter__(self): # -> Self@Py2Iterator:
        ...
    
    def next(self):
        ...
    


def safe_iterator(iterator): # -> Py2Iterator:
    ...

protocol_map = ...