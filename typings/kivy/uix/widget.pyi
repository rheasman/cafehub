from typing import Dict, List, Optional, Tuple, Union

from kivy.properties import AliasProperty, BooleanProperty, NumericProperty, ObjectProperty, ReferenceListProperty, StringProperty
from kivy.core.window import WindowBase

WindowType = Union['Widget', 'WindowBase']
Numeric = Union[int, float]

class WidgetBase: ...


class Widget(WidgetBase):
    center_x: AliasProperty[int]
    center_y: AliasProperty[int]
    center: ReferenceListProperty[Tuple[int, int]]
    disabled: BooleanProperty
    height: NumericProperty
    id: StringProperty
    opacity: NumericProperty
    parent: ObjectProperty['Widget']
    pos: ReferenceListProperty[Tuple[Numeric, Numeric]]
    pos_hint: ObjectProperty[Dict[str, float]]
    right: AliasProperty[int]
    size: ReferenceListProperty[Tuple[int, int]]
    size_hint: ReferenceListProperty[Tuple[float, float]]
    size_hint_min: ReferenceListProperty[Tuple[float, float]]
    size_hint_max: ReferenceListProperty[Tuple[float, float]]
    size_hint_x: NumericProperty
    size_hint_min_x: NumericProperty
    size_hint_max_x: NumericProperty
    size_hint_y: NumericProperty
    size_hint_min_y: NumericProperty
    size_hint_max_y: NumericProperty
    top: AliasProperty[int]
    width: NumericProperty
    x: NumericProperty
    y: NumericProperty

    def add_widget(self, widget: 'Widget', index: Optional[int] = 0, canvas: Optional[str] = None) -> None: ...
    def clear_widgets(self, children: Optional[List['Widget']]) -> None: ...
    def collide_point(self, x: int, y: int) -> bool: ...
    def collide_widget(self, wid: 'Widget') -> bool: ...
    def export_to_png(self, filename: str, flipped: Optional[bool] = False) -> None: ...
    def get_parent_window(self) -> WindowType: ...
    def get_root_window(self) -> WindowType: ...
    def remove_widget(self, widget: 'Widget') -> None: ...
    def to_local(self, x: Numeric, y: Numeric, relative: Optional[bool] = False) -> Tuple[Numeric, Numeric]: ...
    def to_parent(self, x: Numeric, y: Numeric, relative: Optional[bool] = False) -> Tuple[Numeric, Numeric]: ...
    def to_widget(self, x: Numeric, y: Numeric, relative: Optional[bool] = False) -> Tuple[Numeric, Numeric]: ...
    def to_window(self, x: Numeric, y: Numeric, relative: Optional[bool] = False) -> Tuple[Numeric, Numeric]: ...