from typing import Any, Callable, List, Tuple, Union

from kivy.graphics.instructions import RenderContext
from kivy.graphics.texture import Texture

Tuple2i = Tuple[int, int]
Tuple4f = Tuple[float, float, float, float]

class Fbo(RenderContext):
    clear_color: Tuple4f
    pixels: List[bytes]
    size: Tuple2i
    texture: Texture

    def __init__(self,
                 clear_color: Tuple4f = (0, 0, 0, 0),
                 size: Tuple2i = (0, 0),
                 push_viewport: bool = False,
                 with_depthbuffer: bool = False,
                 with_stencilbuffer: bool = False) -> None: ...

    def add_reload_observer(self, callback: Callable[[RenderContext], Any]) -> None: ...
    def bind(self) -> None: ...
    def clear_buffer(self) -> None: ...
    def get_pixel_color(self, wx: int, wy: int) -> Tuple[float, float, float, float]: ...
    def release(self) -> None: ...
    def remove_reload_observer(self, callback: Callable[[RenderContext], Any]) -> None: ...