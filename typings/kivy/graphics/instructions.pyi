from typing import Any, Callable, Union

class Instruction: pass

class InstructionGroup(Instruction):
    def add(self, instruction: Instruction) -> None: ...
    def clear(self) -> None: ...
    def insert(self, index: int, instruction: Instruction) -> None: ...
    def remove(self, instruction: Instruction) -> None: ...
    def remove_group(self, name) -> None: ...

class ContextInstruction(Instruction): pass

class VertexInstruction(Instruction):
    source: str

class CanvasBase(InstructionGroup): pass

class Canvas(CanvasBase):
    after: InstructionGroup
    before: InstructionGroup
    has_after: bool
    has_before: bool
    opacity: Union[int, float]

    def add(self, instruction: Instruction) -> None: ...
    def ask_update(self) -> None: ...
    def clear(self) -> None: ...
    def draw(self) -> None: ...

class RenderContext(Canvas):
    use_parent_modelview: bool
    use_parent_projection: bool

class Callback(Instruction):
    reset_context: bool

    def __init__(self, cb: Callable[[Instruction], Any]) -> None: ...
    def ask_update(self) -> None: ...