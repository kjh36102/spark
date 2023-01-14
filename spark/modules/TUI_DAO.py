from TUI_Widgets import CheckableListItem

class InputRequest:
    def __init__(self, prompt, help_doc='', hint='', essential=False, default='') -> None:
        self.prompt = prompt
        self.help_doc = help_doc
        self.hint = hint
        self.essential = essential
        self.default = default

class Scene:
    def __init__(self, 
                main_prompt='Select what you want.',
                items=[],
                help_prompt='Do you need help?',
                help_title='',
                help_doc='',
                cursor_idx=0) -> None:
        
        self.main_prompt = main_prompt
        self.items = items
        self.help_title = help_title
        self.help_prompt = help_prompt
        self.help_doc = help_doc
        self.current_cursor = cursor_idx

    def add_item(self, item):
        self.items.append(item)
    
    def get_item(self, idx):
        return self.items[idx]
    
    def rebuild_items(self):
        new_items = []
        for item in self.items:
            new_items.append(CheckableListItem(item.value, item.callback, item.callback_args, item.checked, item.show_checkbox))
        self.items = new_items
        
def get_func_names(funcs):
    return [(func.__name__).replace('_', ' ') for func in funcs]