from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from TUI_Widgets import ReactiveLabel, ListContainer

from textual.app import events
from textual.reactive import reactive
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Label, ListItem, Input
from textual.message import Message, MessageTarget

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

    def __init__(self, value,  checked=False, show_checkbox=False) -> None:
        super().__init__()

        self.value = value
        self.checked = checked
        self.show_checkbox = show_checkbox

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
        
class InputContainer(Container):
    
    def __init__(self, prompt='There is no input request.', help_doc='', hint=''):
        
        self.prompt_origin = prompt
        self.help_doc_origin = help_doc
        
        self.prompt = ReactiveLabel(prompt, indent=1, bold=True)
        self.help_doc = ReactiveLabel(help_doc, indent=3)
        self.prompt_container = Container(self.prompt)
        self.help_doc_container = Container(self.help_doc)
        self.input_box = Input()
        self.input_box.placeholder = hint
        
        self.state_display = False
        
        self.expand_state = False
        
        super().__init__(
            self.prompt_container, self.help_doc_container, self.input_box
        )
        
    class Submitted(Message):
        def __init__(self, sender: MessageTarget, value) -> None:
            super().__init__(sender)
            self.value = value
            
    class Aborted(Message):
        def __init__(self, sender: MessageTarget) -> None:
            super().__init__(sender)
        
    async def _on_compose(self) -> None:
        self.hide()
        return await super()._on_compose()
        
    def on_mount(self):
        self.hide()
        self.prompt_container.styles.height = 1
        
        self.clear()
        
    async def _on_idle(self, event: events.Idle) -> None:
        self.resize()
        return await super()._on_idle(event)
    
    BINDINGS = [
        Binding('ctrl+x', 'expand_input_help', 'expand', priority=True),
        Binding('enter', 'submit_input', 'submit', priority=True),
        Binding('ctrl+z', 'abort_input', 'abort', priority=True),
        Binding('escape', 'close_container', 'close', priority=True),
    ]
    
    async def action_close_container(self):
        self.hide()
    
    def action_expand_input_help(self):
        self.expand_state = False if self.expand_state else True
        self.set(self.prompt_origin, self.help_doc_origin, self.input_box.placeholder, preserve_value=True)
        
    async def action_submit_input(self):
        await self.emit(self.Submitted(self, self.input_box.value))
        
    async def action_abort_input(self):
        await self.emit(self.Aborted(self))
        
    def __set(self, prompt, help_doc, hint, password=False, previous=None):
        new_prompt = ReactiveLabel(prompt, indent=1, bold=True)
        new_help_doc = ReactiveLabel(help_doc, indent=3)
        self.input_box.placeholder = hint
      
        self.prompt.remove()
        self.help_doc.remove()
        
        self.prompt_container.mount(new_prompt)
        self.help_doc_container.mount(new_help_doc)
        
        self.prompt = new_prompt
        self.help_doc = new_help_doc
        
        if previous == None: self.input_box.value = ''
        else: self.input_box.value = previous
        
        if help_doc == '': self.help_doc.styles.display = 'none'
        if password: self.input_box.password = True
        else: self.input_box.password = False
        
        
    def set(self, prompt, help_doc='', hint='', password=False, previous=None):
        self.prompt_origin = prompt
        self.help_doc_origin = help_doc
            
        self.__set(self.prompt_origin, self.help_doc_origin, hint, password, previous)

    def clear(self):
        self.prompt_origin = 'There is no input request.'
        self.help_doc_origin = ''
        
        self.__set(self.prompt_origin, self.help_doc_origin, '')
 
    def show(self):
        self.state_display = True
        self.styles.display = 'block'
        self.app.set_focus(self.input_box)
        pass
    
    def hide(self):
        self.state_display = False
        self.styles.display = 'none'
        self.app.action_focus_next()
        pass
    
    def resize(self):
        contents_height = self.prompt_container.size.height + self.help_doc_container.size.height + 3
        
        if not self.expand_state:
            prompt_max_width = self.app.size.width - (self.prompt.indent * 2)
            help_doc_max_width = (self.app.size.width - (self.help_doc.indent * 2)) * 2
            
            if len(self.prompt_origin) > prompt_max_width:
                self.prompt.value = self.prompt_origin[:prompt_max_width - 10] + ' .....'
                
            if len(self.help_doc_origin) > help_doc_max_width:
                self.help_doc.value = self.help_doc_origin[:help_doc_max_width - 15] + ' .....'
        
            self.styles.height = min((self.app.size.height - 2), contents_height)
        else: self.styles.height = contents_height    
            
        self.prompt_container.styles.height = 'auto'
        self.help_doc_container.styles.height = 'auto'
        
class ListContainer(Container):
    def __init__(self, multi_select=False) -> None:
        self.target_scene = None
        super().__init__()
    
    class Selected(Message):
        def __init__(self, sender: MessageTarget, scene) -> None:
            super().__init__(sender)
            self.scene = scene
            
    class Pop(Message):
        def __init__(self, sender: MessageTarget) -> None:
            super().__init__(sender)
            
    class Submitted(Message):
        def __init__(self, sender: MessageTarget, scene) -> None:
            super().__init__(sender)
            self.scene = scene
        
    BINDINGS = [
        Binding('enter', 'submit_items', 'submit', key_display='ENTER', priority=True),
        Binding('space', 'select_item', 'select', key_display='SPACE'),
        Binding('escape', 'press_escape', 'back'),
        Binding('pageup', 'scroll_page_up', 'pageup', priority=True),
        Binding('pagedown', 'scroll_page_down', 'pagedown', priority=True),
        Binding('up', 'scroll_up', 'up', priority=True),
        Binding('down', 'scroll_down', 'down', priority=True),
        Binding('home', 'scroll_home', 'home', priority=True),
        Binding('end', 'scroll_end', 'end', priority=True),
    ]
        
    async def action_select_item(self):
        await self.emit(self.Selected(self, self.target_scene))
        
    async def action_submit_items(self):
        await self.emit(self.Submitted(self, self.target_scene))
        
    async def action_press_escape(self):
        await self.emit(self.Pop(self))
        
    def move_cursor_up(scene, value):
        scene.list_view.index = scene.list_view.index - value
        scene.cursor = scene.list_view.index
        
    def move_cursor_down(scene, value):
        scene.list_view.index = scene.list_view.index + value
        scene.cursor = scene.list_view.index
    
    def move_cursor_to(scene, value):
        scene.list_view.index = value
        scene.cursor = scene.list_view.index
        
    def action_scroll_up(self):
        ListContainer.move_cursor_up(self.target_scene, 1)
        
    def action_scroll_down(self):
        ListContainer.move_cursor_down(self.target_scene, 1)

    def action_scroll_home(self):
        ListContainer.move_cursor_to(self.target_scene, 0)

    def action_scroll_end(self):
        ListContainer.move_cursor_to(self.target_scene, len(self.target_scene.list_view.children) - 1)
        
    def action_scroll_page_up(self):
        unit = int((self.app.size.height - 2) * 0.8)
        ListContainer.move_cursor_up(self.target_scene, unit)
        
    def action_scroll_page_down(self):
        unit = int((self.app.size.height - 2) * 0.8)
        ListContainer.move_cursor_down(self.target_scene, unit)
        

class LoadingBox(ReactiveLabel):
    def __init__(self, ratio=0, msg=''):
        super().__init__('')
        self.styles.width = '100%'
        self.ratio = ratio
        self.msg = msg
        
    def on_mount(self):
        self.set_bar(self.ratio, self.msg)
        
    def __call__(self, ratio, msg):
        self.set_bar(ratio, msg)        
        
    def set_bar(self, ratio, msg):
        if ratio < 0: ratio = 0
        elif ratio > 1: ratio = 1
        self.ratio = ratio
        self.msg = msg
        
        max_width = 20
        bar_len = int(max_width * ratio)
        bar = '■' * bar_len
        remain = ' ' * (max_width - bar_len)
        
        msg_width = self.app.size.width - (max_width + 4)
        if len(msg) > msg_width: fit_msg = msg[:msg_width - 3] + '...'
        else: fit_msg = msg
        
        self.value = '[' + bar + remain + '] ' + fit_msg
        
    def hide(self):
        self.styles.height = 0
        self.styles.display = 'none'
        
    def show(self):
        self.styles.height = 1
        self.styles.display = 'block'
        
    def clear(self):
        self.set_bar(0, '')
        