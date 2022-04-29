from kivy.graphics.instructions import Instruction

class StencilPush(Instruction): pass
class StencilPop(Instruction): pass
class StencilUnUse(Instruction): pass


class StencilUse(Instruction): 
    func_op: str