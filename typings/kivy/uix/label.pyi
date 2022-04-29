from typing import List, Optional, Tuple, Union

from kivy.properties import BooleanProperty, ListProperty, NumericProperty, OptionProperty, ReferenceListProperty, StringProperty
from kivy.uix.widget import Widget

AnyNumber = Union[int, float]

class Label(Widget):
    bold: BooleanProperty
    color: ListProperty[float]
    disabled_color: ListProperty[float]
    disabled_outline_color: ListProperty[float]
    font_size: NumericProperty
    halign: OptionProperty[str]
    markup: BooleanProperty
    padding_x: NumericProperty
    padding_y: NumericProperty
    padding: ReferenceListProperty[Tuple[int, int]]
    text: StringProperty
    text_size: ListProperty[int]

    def __init__(self,
                 text: Optional[str] = '',
                 font_size: Optional[Union[str, int, float]] = '15sp',
                 markup: Optional[bool] = False,
                 halign: Optional[str] = 'left',
                 color: Optional[Tuple[AnyNumber, AnyNumber, AnyNumber, AnyNumber]] = (1, 1, 1, 1)) -> None: ...