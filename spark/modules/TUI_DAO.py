from TUI_Elems import CheckableListItem

class InputRequest:
    def __init__(self, prompt, help_doc='', hint='', default=None, password=False, essential=False, prevalue=''):
        self.prompt = prompt
        self.help_doc = help_doc
        self.hint = hint
        self.default = default
        self.password = password
        self.prevalue = prevalue
        self.essential = essential
        
class Scene:
    def __init__(self, items, main_prompt='Select what you want', help_prompt='Show Help Doc', help_title='', help_doc='', cursor=0, multi_select=False) -> None:
        self.main_prompt = main_prompt
        self.help_prompt = help_prompt
        self.help_title = help_title
        self.help_doc = help_doc
        self.multi_select = multi_select
        self.cursor = cursor
        self.items = [CheckableListItem(item, show_checkbox=multi_select) for item in items]
        self.list_view = None
        self.selected_items = {}
        
def get_func_names(funcs):
    return [(func.__name__).replace('_', ' ') for func in funcs]