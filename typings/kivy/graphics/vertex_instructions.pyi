from typing import Sequence, Tuple

from kivy.graphics.instructions import VertexInstruction

class Rectangle(VertexInstruction):
    pos = Tuple[int, int]
    size = Tuple[int, int]

    def __init__(self, pos: Sequence[int], size: Sequence[int], source: str) -> None: ...