from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from TUI_Widgets import ReactiveLabel, ListContainer
    from TUI_DAO import Scene
    from TUI_Elems import CheckableListItem

from TUI_Elems import *
from TUI_DAO import InputRequest
from textual.app import events
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Input
from textual.message import Message, MessageTarget

import asyncio
from pyautogui import press
        
class InputContainer(Container):
    
    def __init__(self, prompt='There is no input request.', help_doc='', hint=''):
        
        self.prompt_origin = prompt
        self.help_doc_origin = help_doc
        
        self.prompt = ReactiveLabel(prompt, indent=1, bold=True)
        self.help_doc = ReactiveLabel(help_doc, indent=3)
        self.prompt_container = Container(self.prompt)
        self.help_doc_container = Container(self.help_doc)
        self.input_box = Input()

        self.current_request = None        
        self.state_display = False
        self.expand_state = False
        
        self.input_box.placeholder = hint
        
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
        self.help_doc_container.styles.display = 'none'
        self.clear()
        
    async def _on_idle(self, event: events.Idle) -> None:
        self.resize()
        return await super()._on_idle(event)
    
    BINDINGS = [
        Binding('ctrl+x', 'expand_input_help', 'expand/shrink', priority=True),
        Binding('enter', 'submit_input', 'submit', priority=True),
        Binding('ctrl+z', 'abort_input', 'abort', priority=True),
        Binding('escape', 'close_container', 'close', priority=True),
    ]
    
    async def action_close_container(self):
        self.hide()
    
    def action_expand_input_help(self):
        # expand_binding = [binding for binding in self.BINDINGS if binding.key == 'ctrl+x'][0]
        if self.expand_state: 
            self.expand_state = False
            # expand_binding.key_display = 'expand'
        else:
            self.expand_state = True
            # expand_binding.key_display = 'shrink'
            self.set(
                InputRequest(
                    prompt=self.prompt_origin,
                    help_doc=self.help_doc_origin,
                    hint=self.input_box.placeholder,
                    essential=self.current_request.essential,
                    password=self.current_request.password,
                    prevalue=self.input_box.value
                )
            )
            
            self.prompt_container.styles.height = self.prompt.size.height
            self.help_doc_container.styles.height = self.help_doc.size.height
        
    async def action_submit_input(self):
        if self.current_request.essential:
            if self.input_box.value == '': return
        else:
            if self.current_request.default != None:
                self.input_box.value = self.current_request.default
        
        await self.emit(self.Submitted(self, self.input_box.value))
        
    async def action_abort_input(self):
        await self.emit(self.Aborted(self))
        
    def set(self, input_request:InputRequest):
        self.current_request = input_request
        
        self.prompt_origin = input_request.prompt
        self.help_doc_origin = input_request.help_doc
        
        self.prompt.value = input_request.prompt
        self.help_doc.value = input_request.help_doc
        self.input_box.placeholder = input_request.hint
        
        self.input_box.password = input_request.password
        self.help_doc_container.styles.display = 'none' if input_request.help_doc == '' else 'block'
        
        if input_request.prevalue != '': 
            self.input_box.value = input_request.prevalue
            
    def clear(self):
        self.prompt_origin = 'There is no input request.'
        self.help_doc_origin = ''
        
        self.input_box.value = ''
        self.set(InputRequest(prompt=self.prompt_origin))
 
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
    def __init__(self) -> None:
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
        # Binding('ctrl+s', 'search_item', 'search', priority=True),
        Binding('ctrl+a', 'select_all', 'check all', priority=True),
        Binding('ctrl+x', 'deselect_all', 'uncheck all', priority=True),
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
    
    #TODO 검색기능 추가해보기
    # async def action_search_item(self):
    #     #검색 요청 띄우기
    #     await asyncio.create_task(self.app.target_process.request_search())
    
    async def action_select_all(self):
        for idx, child in enumerate(self.target_scene.list_view.children):
            child.check()
            self.target_scene.selected_items[idx] = child.value
            
    async def action_deselect_all(self):
        for _, child in enumerate(self.target_scene.list_view.children):
            child.uncheck()
            self.target_scene.selected_items.clear()
        
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
        self.show_state = False
        
    def on_mount(self):
        self.set_ratio(self.ratio, self.msg)
        
    def set_ratio(self, ratio, msg):
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
        self.show_state = False
        
    def show(self):
        self.styles.height = 1
        self.styles.display = 'block'
        self.show_state = True
        
    def clear(self):
        self.set_ratio(0, '')
        