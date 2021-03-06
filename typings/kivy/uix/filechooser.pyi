"""
This type stub file was generated by pyright.
"""

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.app import App

'''
FileChooser
===========

The Fi'''
__all__ = ('FileChooserListView', 'FileChooserIconView', 'FileChooserListLayout', 'FileChooserIconLayout', 'FileChooser', 'FileChooserController', 'FileChooserProgressBase', 'FileSystemAbstract', 'FileSystemLocal')
platform = ...
filesize_units = ...
_have_win32file = ...
if platform == 'win':
    ...
def alphanumeric_folders_first(files, filesystem): # -> list[Unknown]:
    ...

class FileSystemAbstract:
    '''Class for implementing a File Sy'''
    def listdir(self, fn): # -> None:
        '''Return the list of files in the '''
        ...
    
    def getsize(self, fn): # -> None:
        '''Return the size in bytes of a fi'''
        ...
    
    def is_hidden(self, fn): # -> None:
        '''Return True if the file is hidde'''
        ...
    
    def is_dir(self, fn): # -> None:
        '''Return True if the argument pass'''
        ...
    


class FileSystemLocal(FileSystemAbstract):
    '''Implementation of :class:`FileSy'''
    def listdir(self, fn): # -> list[str]:
        ...
    
    def getsize(self, fn): # -> int:
        ...
    
    def is_hidden(self, fn): # -> bool:
        ...
    
    def is_dir(self, fn): # -> bool:
        ...
    


class FileChooserProgressBase(FloatLayout):
    '''Base for implementing a progress'''
    path = ...
    index = ...
    total = ...
    def cancel(self, *largs): # -> None:
        '''Cancel any action from the FileC'''
        ...
    
    def on_touch_down(self, touch): # -> Literal[True] | None:
        ...
    
    def on_touch_move(self, touch): # -> Literal[True] | None:
        ...
    
    def on_touch_up(self, touch): # -> Literal[True] | None:
        ...
    


class FileChooserProgress(FileChooserProgressBase):
    ...


class FileChooserLayout(FloatLayout):
    '''Base class for file chooser layo'''
    VIEWNAME = ...
    __events__ = ...
    controller = ...
    def on_entry_added(self, node, parent=...): # -> None:
        ...
    
    def on_entries_cleared(self): # -> None:
        ...
    
    def on_subentry_to_entry(self, subentry, entry): # -> None:
        ...
    
    def on_remove_subentry(self, subentry, entry): # -> None:
        ...
    
    def on_submit(self, selected, touch=...): # -> None:
        ...
    


class FileChooserListLayout(FileChooserLayout):
    '''File chooser layout using a list'''
    VIEWNAME = ...
    _ENTRY_TEMPLATE = ...
    def __init__(self, **kwargs) -> None:
        ...
    
    def scroll_to_top(self, *args): # -> None:
        ...
    


class FileChooserIconLayout(FileChooserLayout):
    '''File chooser layout using an ico'''
    VIEWNAME = ...
    _ENTRY_TEMPLATE = ...
    def __init__(self, **kwargs) -> None:
        ...
    
    def scroll_to_top(self, *args): # -> None:
        ...
    


class FileChooserController(RelativeLayout):
    '''Base for implementing a FileChoo'''
    _ENTRY_TEMPLATE = ...
    layout = ...
    path = ...
    filters = ...
    filter_dirs = ...
    sort_func = ...
    files = ...
    show_hidden = ...
    selection = ...
    multiselect = ...
    dirselect = ...
    rootpath = ...
    progress_cls = ...
    file_encodings = ...
    file_system = ...
    font_name = ...
    _update_files_ev = ...
    _create_files_entries_ev = ...
    __events__ = ...
    def __init__(self, **kwargs) -> None:
        ...
    
    def on_touch_down(self, touch): # -> Literal[True] | None:
        ...
    
    def on_touch_up(self, touch): # -> Literal[True] | None:
        ...
    
    def on_entry_added(self, node, parent=...): # -> None:
        ...
    
    def on_entries_cleared(self): # -> None:
        ...
    
    def on_subentry_to_entry(self, subentry, entry): # -> None:
        ...
    
    def on_remove_subentry(self, subentry, entry): # -> None:
        ...
    
    def on_submit(self, selected, touch=...): # -> None:
        ...
    
    def entry_touched(self, entry, touch):
        '''(internal) This method must be c'''
        ...
    
    def entry_released(self, entry, touch):
        '''(internal) This method must be c'''
        ...
    
    def open_entry(self, entry): # -> None:
        ...
    
    def get_nice_size(self, fn): # -> str | None:
        '''Pass the filepath. Returns the s'''
        ...
    
    def cancel(self, *largs): # -> None:
        '''Cancel any background action sta'''
        ...
    
    def entry_subselect(self, entry): # -> None:
        ...
    
    def close_subselection(self, entry): # -> None:
        ...
    


class FileChooserListView(FileChooserController):
    '''Implementation of a :class:`File'''
    _ENTRY_TEMPLATE = ...


class FileChooserIconView(FileChooserController):
    '''Implementation of a :class:`File'''
    _ENTRY_TEMPLATE = ...


class FileChooser(FileChooserController):
    '''Implementation of a :class:`File'''
    manager = ...
    _view_list = ...
    def get_view_list(self): # -> List[Unknown]:
        ...
    
    view_list = ...
    _view_mode = ...
    def get_view_mode(self): # -> str:
        ...
    
    def set_view_mode(self, mode): # -> None:
        ...
    
    view_mode = ...
    def __init__(self, **kwargs) -> None:
        ...
    
    def add_widget(self, widget, *args, **kwargs): # -> None:
        ...
    
    def rebuild_views(self): # -> None:
        ...
    
    def update_view(self, *args): # -> None:
        ...
    
    def on_entry_added(self, node, parent=...): # -> None:
        ...
    
    def on_entries_cleared(self): # -> None:
        ...
    
    def on_subentry_to_entry(self, subentry, entry): # -> None:
        ...
    
    def on_remove_subentry(self, subentry, entry): # -> None:
        ...
    
    def on_submit(self, selected, touch=...): # -> None:
        ...
    


if __name__ == '__main__':
    root = ...
    class FileChooserApp(App):
        def build(self):
            ...
        
    
    
