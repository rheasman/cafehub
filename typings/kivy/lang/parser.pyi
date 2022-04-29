"""
This type stub file was generated by pyright.
"""

'''
Parser
======

Class used for t'''
__all__ = ('Parser', 'ParserException')
trace = ...
global_idmap = ...
__KV_INCLUDES__ = ...
str_re = ...
lang_str = ...
lang_fstr = ...
lang_key = ...
lang_keyvalue = ...
lang_tr = ...
lang_cls_split_pat = ...
_handlers = ...
class ProxyApp:
    __slots__ = ...
    def __init__(self) -> None:
        ...
    
    def __getattribute__(self, name): # -> Any:
        ...
    
    def __delattr__(self, name): # -> None:
        ...
    
    def __setattr__(self, name, value): # -> None:
        ...
    
    def __bool__(self): # -> bool:
        ...
    
    def __str__(self) -> str:
        ...
    
    def __repr__(self): # -> str:
        ...
    


class ParserException(Exception):
    '''Exception raised when something '''
    def __init__(self, context, line, message, cause=...) -> None:
        ...
    


class ParserRuleProperty:
    '''Represent a property inside a ru'''
    __slots__ = ...
    def __init__(self, ctx, line, name, value, ignore_prev=...) -> None:
        ...
    
    def precompile(self): # -> None:
        ...
    
    @classmethod
    def get_names_from_expression(cls, node):
        """
        Look for all the symbol"""
        ...
    
    def __repr__(self): # -> str:
        ...
    


class ParserRule:
    '''Represents a rule, in terms of t'''
    __slots__ = ...
    def __init__(self, ctx, line, name, level) -> None:
        ...
    
    def precompile(self): # -> None:
        ...
    
    def create_missing(self, widget): # -> None:
        ...
    
    def __repr__(self): # -> str:
        ...
    


class Parser:
    '''Create a Parser object to parse '''
    PROP_ALLOWED = ...
    CLASS_RANGE = ...
    PROP_RANGE = ...
    __slots__ = ...
    def __init__(self, **kwargs) -> None:
        ...
    
    def execute_directives(self): # -> None:
        ...
    
    def parse(self, content): # -> None:
        '''Parse the contents of a Parser f'''
        ...
    
    def strip_comments(self, lines): # -> None:
        '''Remove all comments from all lin'''
        ...
    
    def parse_level(self, level, lines, spaces=...):
        '''Parse the current level (level *'''
        ...
    


class ParserSelector:
    def __init__(self, key) -> None:
        ...
    
    def match(self, widget):
        ...
    
    def __repr__(self): # -> str:
        ...
    


class ParserSelectorClass(ParserSelector):
    def match(self, widget): # -> bool:
        ...
    


class ParserSelectorName(ParserSelector):
    parents = ...
    def get_bases(self, cls): # -> Generator[Unknown, None, None]:
        ...
    
    def match(self, widget): # -> bool:
        ...
    
    def match_rule_name(self, rule_name):
        ...
    

