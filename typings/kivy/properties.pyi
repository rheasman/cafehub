from typing import Any, Callable, Generic, Mapping, List, Optional, Sequence, Tuple, TypeVar, Union

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')
AnyNumber = TypeVar('AnyNumber', int, float, str) # Yes Kivy properties accept strings as numbers

class Property(Generic[T]):
    def __init__(self,
                 default: Optional[T] = None,
                 errorhandler: Optional[Callable[..., T]] = None,
                 errorvalue: Optional[T] = None,
                 force_dispatch: bool = False) -> None: ...
    def bind(self,
             **kwargs: Mapping[str, Callable[[T, Any], Any]]) -> None: ...
    def unbind(self,
               **kwargs: Mapping[str, Callable[[T, Any], Any]]) -> None: ...

    def __get__(self, inst: Any, own: Any) -> T: ...
    def __set__(self, inst: Any, value: T) -> None: ...

class BooleanProperty(Property[bool]): ...

class NumericProperty(Property[AnyNumber]): ...

class DictProperty(Property[Mapping[K, V]]): ...

class StringProperty(Property[str]): ...

class ListProperty(Property[List[V]]): ...

class ObjectProperty(Property[V]): ...

class BoundedNumericProperty(Property[AnyNumber]):
    def __init__(self,
                 default: Optional[T] = None,
                 min: Optional[AnyNumber] = None,
                 max: Optional[AnyNumber] = None,
                 errorhandler: Optional[Callable[..., T]] = None,
                 errorvalue: Optional[T] = None,
                 force_dispatch: Optional[bool] = False) -> None: ...
    
    def get_min(self) -> AnyNumber: ...
    def get_max(self) -> AnyNumber: ...
    def set_min(self, new_value: AnyNumber) -> None: ...
    def set_max(self, new_value: AnyNumber) -> None: ...

class OptionProperty(Property[T]):
    options: List[T]

    def __init__(self,
                 default: T,
                 options: List[T],
                 errorhandler: Optional[Callable[..., T]] = None,
                 errorvalue: Optional[T] = None,
                 force_dispatch: Optional[bool] = False) -> None: ...

AnyTuple = TypeVar('AnyTuple', bound=Tuple[Any, ...])
class ReferenceListProperty(Generic[AnyTuple]):
    def __init__(self,
                 *args: Property[Any],
                 force_dispatch: bool = False) -> None: ...

class AliasProperty(Property[T]):
    def __init__(self,
                 getter: Callable[..., T],
                 setter: Callable[[T], None],
                 bind: Optional[Sequence[str]] = [],
                 cache: Optional[bool] = False,
                 rebind: Optional[bool] = False) -> None: ...

ListOrValue = Union[List[V], V]

class VariableListProperty(Property[List[V]]):
    def __init__(self,
                 default: Optional[ListOrValue],
                 length: Optional[int]) -> None: ...