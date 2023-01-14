from TUI_Widgets import CheckableListItem

class InputRequest:
    def __init__(self, prompt, help_doc, hint) -> None:
        self.prompt = prompt
        self.help_doc = help_doc
        self.hint = hint

class Scene:
    def __init__(self, 
                items=[],
                main_prompt='Select what you want.',
                help_prompt='Do you need help?',
                help_title='Empty help title',
                help_doc='Empty help doc',
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