"""
This type stub file was generated by pyright.
"""

from kivy.event import EventDispatcher

'''
Animation
=========

:class:`An'''
__all__ = ('Animation', 'AnimationTransition')
class Animation(EventDispatcher):
    '''Create an animation definition t'''
    _update_ev = ...
    _instances = ...
    __events__ = ...
    def __init__(self, **kw) -> None:
        ...
    
    @property
    def duration(self): # -> float:
        '''Return the duration of the anima'''
        ...
    
    @property
    def transition(self): # -> str | Any:
        '''Return the transition of the ani'''
        ...
    
    @property
    def animated_properties(self): # -> dict[str, Unknown]:
        '''Return the properties used to an'''
        ...
    
    @staticmethod
    def stop_all(widget, *largs): # -> None:
        '''Stop all animations that concern'''
        ...
    
    @staticmethod
    def cancel_all(widget, *largs): # -> None:
        '''Cancel all animations that conce'''
        ...
    
    def start(self, widget): # -> None:
        '''Start the animation on a widget.'''
        ...
    
    def stop(self, widget): # -> None:
        '''Stop the animation previously ap'''
        ...
    
    def cancel(self, widget): # -> None:
        '''Cancel the animation previously '''
        ...
    
    def stop_property(self, widget, prop): # -> None:
        '''Even if an animation is running,'''
        ...
    
    def cancel_property(self, widget, prop): # -> None:
        '''Even if an animation is running,'''
        ...
    
    def have_properties_to_animate(self, widget): # -> Literal[True] | None:
        '''Return True if a widget still ha'''
        ...
    
    def on_start(self, widget): # -> None:
        ...
    
    def on_progress(self, widget, progress): # -> None:
        ...
    
    def on_complete(self, widget): # -> None:
        ...
    
    def __add__(self, animation): # -> Sequence:
        ...
    
    def __and__(self, animation): # -> Parallel:
        ...
    


class CompoundAnimation(Animation):
    def stop_property(self, widget, prop): # -> None:
        ...
    
    def cancel(self, widget): # -> None:
        ...
    
    def cancel_property(self, widget, prop): # -> None:
        '''Even if an animation is running,'''
        ...
    
    def have_properties_to_animate(self, widget):
        ...
    
    @property
    def animated_properties(self): # -> ChainMap[Any, Any]:
        ...
    
    @property
    def transition(self):
        ...
    


class Sequence(CompoundAnimation):
    def __init__(self, anim1, anim2) -> None:
        ...
    
    @property
    def duration(self):
        ...
    
    def stop(self, widget): # -> None:
        ...
    
    def start(self, widget): # -> None:
        ...
    
    def on_anim1_complete(self, instance, widget): # -> None:
        ...
    
    def on_anim1_progress(self, instance, widget, progress): # -> None:
        ...
    
    def on_anim2_complete(self, instance, widget): # -> None:
        '''Repeating logic used with boolea'''
        ...
    
    def on_anim2_progress(self, instance, widget, progress): # -> None:
        ...
    


class Parallel(CompoundAnimation):
    def __init__(self, anim1, anim2) -> None:
        ...
    
    @property
    def duration(self):
        ...
    
    def stop(self, widget): # -> None:
        ...
    
    def start(self, widget): # -> None:
        ...
    
    def on_anim_complete(self, instance, widget): # -> None:
        ...
    


class AnimationTransition:
    '''Collection of animation function'''
    @staticmethod
    def linear(progress):
        '''.. image:: images/anim_linear.pn'''
        ...
    
    @staticmethod
    def in_quad(progress):
        '''.. image:: images/anim_in_quad.p'''
        ...
    
    @staticmethod
    def out_quad(progress):
        '''.. image:: images/anim_out_quad.'''
        ...
    
    @staticmethod
    def in_out_quad(progress):
        '''.. image:: images/anim_in_out_qu'''
        ...
    
    @staticmethod
    def in_cubic(progress):
        '''.. image:: images/anim_in_cubic.'''
        ...
    
    @staticmethod
    def out_cubic(progress):
        '''.. image:: images/anim_out_cubic'''
        ...
    
    @staticmethod
    def in_out_cubic(progress):
        '''.. image:: images/anim_in_out_cu'''
        ...
    
    @staticmethod
    def in_quart(progress):
        '''.. image:: images/anim_in_quart.'''
        ...
    
    @staticmethod
    def out_quart(progress):
        '''.. image:: images/anim_out_quart'''
        ...
    
    @staticmethod
    def in_out_quart(progress):
        '''.. image:: images/anim_in_out_qu'''
        ...
    
    @staticmethod
    def in_quint(progress):
        '''.. image:: images/anim_in_quint.'''
        ...
    
    @staticmethod
    def out_quint(progress):
        '''.. image:: images/anim_out_quint'''
        ...
    
    @staticmethod
    def in_out_quint(progress):
        '''.. image:: images/anim_in_out_qu'''
        ...
    
    @staticmethod
    def in_sine(progress): # -> float:
        '''.. image:: images/anim_in_sine.p'''
        ...
    
    @staticmethod
    def out_sine(progress): # -> float:
        '''.. image:: images/anim_out_sine.'''
        ...
    
    @staticmethod
    def in_out_sine(progress): # -> float:
        '''.. image:: images/anim_in_out_si'''
        ...
    
    @staticmethod
    def in_expo(progress): # -> float | Literal[1]:
        '''.. image:: images/anim_in_expo.p'''
        ...
    
    @staticmethod
    def out_expo(progress): # -> float:
        '''.. image:: images/anim_out_expo.'''
        ...
    
    @staticmethod
    def in_out_expo(progress): # -> float:
        '''.. image:: images/anim_in_out_ex'''
        ...
    
    @staticmethod
    def in_circ(progress): # -> float:
        '''.. image:: images/anim_in_circ.p'''
        ...
    
    @staticmethod
    def out_circ(progress): # -> float:
        '''.. image:: images/anim_out_circ.'''
        ...
    
    @staticmethod
    def in_out_circ(progress): # -> float:
        '''.. image:: images/anim_in_out_ci'''
        ...
    
    @staticmethod
    def in_elastic(progress): # -> float:
        '''.. image:: images/anim_in_elasti'''
        ...
    
    @staticmethod
    def out_elastic(progress): # -> float:
        '''.. image:: images/anim_out_elast'''
        ...
    
    @staticmethod
    def in_out_elastic(progress): # -> float:
        '''.. image:: images/anim_in_out_el'''
        ...
    
    @staticmethod
    def in_back(progress):
        '''.. image:: images/anim_in_back.p'''
        ...
    
    @staticmethod
    def out_back(progress):
        '''.. image:: images/anim_out_back.'''
        ...
    
    @staticmethod
    def in_out_back(progress):
        '''.. image:: images/anim_in_out_ba'''
        ...
    
    @staticmethod
    def in_bounce(progress):
        '''.. image:: images/anim_in_bounce'''
        ...
    
    @staticmethod
    def out_bounce(progress):
        '''.. image:: images/anim_out_bounc'''
        ...
    
    @staticmethod
    def in_out_bounce(progress):
        '''.. image:: images/anim_in_out_bo'''
        ...
    

