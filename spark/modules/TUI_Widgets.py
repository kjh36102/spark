from textual.widgets import Label, ListItem
from textual.reactive import reactive

class ReactiveLabel(Label):
    value = reactive('')
    
    def __init__(self, value, shrink=True, indent=0, bold=False) :
        super().__init__(shrink=shrink)
        self.indent = indent
        
        self.styles.height = 'auto'
        self.styles.width = '100%'
        self.styles.margin = (0, indent, 0, indent)
        self.styles.text_style = 'bold' if bold else 'none'
        self.set_text(value)
        
    def __call__(self, value):
        self.set_text(value)
        
    def set_text(self, value):
        self.value = value
    
    def render(self):
        return self.value

class Prompt(ReactiveLabel):
    def __init__(self, value) :
        super().__init__(value)
        
        #styles
        self.styles.background = '#0053aa'
        self.styles.width = '100%'
        self.styles.text_style = 'bold'
        
    def render(self):
        return '  ' + self.value
    
class CheckableListItem(ListItem):
    SYMBOL_UNCHECK = '[ ]'
    SYMBOL_CHECK = '[+]'
    check_box = reactive('[ ]')
    value = ReactiveLabel('')

    def __init__(self, value, callback=lambda x:x, callback_args=(), checked=False, show_checkbox=True) -> None:
        super().__init__()

        self.value = value
        self.checked = checked
        self.show_checkbox = show_checkbox
        self.callback = self.toggle_check if show_checkbox else callback
        self.callback_args = callback_args

        if checked: self.check_box = self.SYMBOL_CHECK
        
    def render(self):
        if self.show_checkbox: return f' {self.check_box}  {self.value}'
        else: return f' >  {self.value}'
    
    def toggle_check(self, app, item):
        if self.checked: self.uncheck()
        else: self.check()
    
    def check(self):
        self.check_box = self.SYMBOL_CHECK
        self.checked = True
    
    def uncheck(self):
        self.check_box = self.SYMBOL_UNCHECK
        self.checked = False