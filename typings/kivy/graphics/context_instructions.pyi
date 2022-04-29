from typing import Optional, overload, Sequence, Tuple, Union

from kivy.graphics.instructions import ContextInstruction

Tuple2f = Tuple[float, float]
Tuple3f = Tuple[float, float, float]
Tuple4f = Tuple[float, float, float, float]


class Color(ContextInstruction):
    r: float
    g: float
    b: float
    h: float
    s: float
    v: float
    a: float
    rgb: Tuple3f
    rgba: Tuple4f
    hsv: Tuple3f
    hsva: Tuple4f

    @overload
    def __init__(self, r: float, g: float, b: float, mode: Optional[str] = 'rgb') -> None: ...

    @overload
    def __init__(self, r: float, g: float, b: float, a: float, mode: Optional[str] = 'rgb') -> None: ...


class BindTexture(ContextInstruction):
    # TODO implement
    ...


Numeric = Union[int, float]

Matrix = Tuple[
    Numeric, Numeric, Numeric, Numeric,
    Numeric, Numeric, Numeric, Numeric,
    Numeric, Numeric, Numeric, Numeric,
    Numeric, Numeric, Numeric, Numeric
]

class MatrixInstruction(ContextInstruction):
    matrix: Matrix
    stack: str

class PushMatrix(MatrixInstruction): pass


class PopMatrix(MatrixInstruction): pass


class Transform(ContextInstruction): pass


class Rotate(Transform):
    angle: Numeric
    axis: Tuple3f
    origin: Union[Tuple2f, Tuple3f]
    
    def set(self, angle: int, axisx: float, axisy: float, axisz: float) -> None: ...


class Scale(Transform):
    origin: Union[Tuple3f, Tuple2f]
    scale: Tuple3f
    x: Numeric
    y: Numeric
    z: Numeric
    xyz: Tuple3f

class Translate(Transform):
    x: Numeric
    y: Numeric
    z: Numeric
    xy: Tuple2f
    xyz: Tuple3f