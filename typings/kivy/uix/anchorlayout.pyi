from typing import List, Optional

from kivy.properties import OptionProperty, VariableListProperty
from kivy.uix.layout import Layout

class AnchorLayout(Layout):
    anchor_x: OptionProperty[str]
    anchor_y: OptionProperty[str]
    padding: VariableListProperty[int]

    def __init__(self,
                 anchor_x: Optional[str] = 'center',
                 anchor_y: Optional[str] = 'center',
                 padding: Optional[List[int]] = [0, 0, 0, 0]) -> None: ...