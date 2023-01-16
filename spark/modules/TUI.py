from textual.app import App, events
from textual.binding import Binding
from textual.screen import Screen
from textual.containers import Container
from textual.widgets import Label, Footer, ListView, TextLog, Input, Button
from textual.containers import Grid
from textual.message import Message, MessageTarget

from TUI_events import *
# from TUI_DAO import *
from TUI_Widgets import ReactiveLabel, Prompt, CheckableListItem

from pyautogui import press


DUMMY_LONG = '''\
Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.
Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section 1.10.32.
Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.
Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section 1.10.32.\
'''

DUMMY_SHROT = '''\
Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.\
'''


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


class HelpScreen(Screen):
    def __init__(self, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name, id, classes)
        
        self.prompt = Prompt('Empty prompt.')
        self.resize_flag = False
    
    def compose(self):
        yield self.prompt
        yield Footer()
        
    async def _on_resize(self, event: events.Resize) -> None:
        self.resize()
        return await super()._on_resize(event)
        
    BINDINGS = [
        Binding('escape', 'pop_screen()', 'back'),
        Binding('up', 'scroll_up', 'up'),
        Binding('down', 'scroll_down', 'down'),
        Binding('pageup', 'scroll_page_up', 'pageup'),
        Binding('pagedown', 'scroll_page_down', 'pagedown'),
        Binding('home', 'scroll_home', 'home'),
        Binding('end', 'scroll_end', 'end'),
    ]
    
    def set(self, prompt, help_title, help_doc):
        try: self.contents_container.remove()
        except AttributeError: pass
        
        self.prompt.value = prompt
        
        self.help_title = ReactiveLabel(help_title, indent=1, bold=True)
        self.help_title_container = Container(self.help_title)
        
        self.help_doc = ReactiveLabel(help_doc, indent=3)
        self.help_doc_container = Container(self.help_doc)
        
        self.contents_container = Container(self.help_title_container, self.help_doc_container)
        
        self.mount(self.contents_container)
        
        self.help_title_container.styles.height = self.help_doc_container.styles.height = 'auto'
        
        self.resize_flag = True
    
    #essential
    async def _on_idle(self, event: events.Idle) -> None:
        self.resize()
        return await super()._on_idle(event)
    
    def action_scroll_up(self):
        self.contents_container.action_scroll_up()
        
    def action_scroll_down(self):
        self.contents_container.action_scroll_down()
        
    def action_scroll_home(self):
        self.contents_container.action_scroll_home()
        
    def action_scroll_end(self):
        self.contents_container.action_scroll_end()
        
    def action_scroll_page_up(self):
        unit = int((self.app.size.height - 2) * 0.8)
        for _ in range(unit): self.contents_container.action_scroll_up()
        
    def action_scroll_page_down(self):
        unit = int((self.app.size.height - 2) * 0.8)
        for _ in range(unit): self.contents_container.action_scroll_down()
    
    def resize(self):
        try:
            self.help_title_container.styles.height = self.help_title.size.height
            self.help_doc_container.styles.height = self.help_doc.size.height
            self.contents_container.styles.height = self.app.size.height - 2
        except AttributeError: pass

    def clear(self):
        self.prompt.value = ''
        self.help_title.value = ''
        self.help_doc.value = ''

class LoggerScreen(Screen):
    def __init__(self, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name, id, classes)
        
        self.prompt = Prompt('Empty prompt.')
        self.logger = TextLog(max_lines=200, wrap=True)
        self.loading_box = LoadingBox()
        
    def compose(self):
        yield self.prompt
        yield self.logger
        yield self.loading_box
        yield Footer()
        
    def on_mount(self):
        self.close_loading_box()
        self.logger._automatic_refresh()
        
    async def _on_resize(self, event: events.Resize) -> None:
        
        self.logger.styles.height = self.app.size.height - 2
        
        return await super()._on_resize(event)
        
    BINDINGS = [
        Binding('ctrl+a', 'test1', 'test1'),
        Binding('escape', 'pop_screen()', 'back'),
        Binding('up', 'scroll_up', 'up'),
        Binding('down', 'scroll_down', 'down'),
        Binding('pageup', 'scroll_page_up', 'pageup'),
        Binding('pagedown', 'scroll_page_down', 'pagedown'),
        Binding('home', 'scroll_home', 'home'),
        Binding('end', 'scroll_end', 'end'),
    ]
    
    def action_scroll_up(self):
        self.logger.action_scroll_up()
        
    def action_scroll_down(self):
        self.logger.action_scroll_down()
        
    def action_scroll_home(self):
        self.logger.action_scroll_home()
        
    def action_scroll_end(self):
        self.logger.action_scroll_end()
        
    def action_scroll_page_up(self):
        unit = int((self.app.size.height - 2) * 0.8)
        for _ in range(unit): self.logger.action_scroll_up()
        
    def action_scroll_page_down(self):
        unit = int((self.app.size.height - 2) * 0.8)
        for _ in range(unit): self.logger.action_scroll_down()
    
    def action_test1(self):
        self.print('hello world')
        
    def open_loading_box(self):
        self.logger.styles.height = self.app.size.height - 3
        self.loading_box.show()
        
    def close_loading_box(self):
        self.logger.styles.height = self.app.size.height - 2
        self.loading_box.hide()
        
    def print(self, text):
        self.logger.write(text)


class MainScreen(Screen):
    
    def __init__(self, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name, id, classes)
        self.prompt = Prompt('Empty prompt')
        self.input_container = InputContainer()
        self.list_container = ListContainer()
        self.contents_container = Container(self.input_container, self.list_container)
        # self.scene_stack = []
        self.multi_select_items = {}

    def compose(self):
        yield self.prompt
        yield self.contents_container
        yield Footer()
        
    BINDINGS = [
        Binding('i', 'toggle_input_container', 'toggle input'),
        Binding('l', 'push_screen("logger")', 'open logger'),
        Binding('h', 'open_help', 'open help'),
        Binding('r', 'release_focus', 'release focus'),
    ]
    
    def action_open_help(self):
        self.app.push_screen(self.app.help_screen)
        pass

    def action_toggle_input_container(self):
        if self.input_container.state_display == False: 
            self.input_container.show()
        else: 
            self.input_container.hide()
            
    def action_release_focus(self):
        self.app.set_focus(None)
        
class AlertScreen(Screen):
    BINDINGS = [
        Binding('space', 'space', 'OK', key_display='SPACE', priority=True),
        Binding('enter', 'enter', '', show=False, priority=True),
        Binding('escape', 'escape', '', show=False, priority=True),
    ]

    def action_space(self):
        self.button.press()
    
    def action_enter(self):
        self.button.press()
        
    def action_escape(self):
        self.button.press()

    def __init__(self, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name, id, classes)

        self.prompt = Prompt('Alert')
        self.label = ReactiveLabel("Empty contents")
        self.button = Button("OK", variant="primary", id='ok_btn')
        self.grid = Grid(self.label, self.button)

        self.grid.styles.grid_size_columns = 1
        self.grid.styles.grid_gutter_horizontal = 2
        self.grid.styles.grid_gutter_vertical = 1

        self.label.styles.background = None
        self.label.styles.width = '100%'
        self.label.styles.height = '100%'
        self.label.styles.content_align = ('center', 'bottom')

        self.button.styles.content_align = ('center', 'bottom')
        self.button.styles.width = 10

    def compose(self):
        yield self.prompt
        yield self.grid
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.pop_screen()
        self.app.action_focus_next()

    async def _on_resize(self, event: events.Resize) -> None:
        self.button.styles.margin = (0, 0, 0, int(((self.app.size.width) - self.button.size.width) / 2))
        return await super()._on_resize(event)
    
    def set(self, prompt, text):
        self.prompt.value = prompt
        self.label.value = text

class TUIApp(App):
    
    def __init__(self):
        super().__init__()
        self.main_screen = MainScreen()
        self.logger_screen = LoggerScreen()
        self.help_screen = HelpScreen()
        self.alert_screen = AlertScreen()
                
        self.target_process = None
        self.current_scene = None

    def on_mount(self):
        #install main screen
        self.install_screen(self.main_screen, name='main')
        
        #install logger screen
        self.install_screen(self.logger_screen, name='logger')
        
        #install help screen
        self.install_screen(self.help_screen, name='help')
        
        #install alert screen
        self.install_screen(self.alert_screen, name='alert')
        
        #push main screen
        self.push_screen('main')
    
    def on_list_container_pop(self, message: ListContainer.Pop):
        self.target_process.abort_select()
        
    async def on_list_container_selected(self, message: ListContainer.Selected):
        #if process waiting input, abort input
        if self.target_process.is_waiting_input: 
            self.target_process.abort_input()
        
        scene = message.scene
        
        idx = scene.list_view.index
        selected_item:CheckableListItem = scene.list_view.children[idx]
        
        if scene.multi_select:
            #check item and add to selected items buffer
            if selected_item.checked:
                selected_item.uncheck()
                scene.selected_items.pop(idx)
            else:
                selected_item.check()
                scene.selected_items[idx] = selected_item
        else: self.target_process.response_select((idx, selected_item.value))
        
    def on_list_container_submitted(self, message: ListContainer.Submitted):
        
        # if process waiting input, abort input
        if self.target_process.is_waiting_input: 
            self.target_process.abort_input()
        
        scene = message.scene
        
        if scene.multi_select:
            self.target_process.response_select(scene.selected_items)
        
    def on_input_container_submitted(self, message: InputContainer.Submitted):
            if self.target_process.is_waiting_input:
                self.target_process.response_input(message.value)
    
    def on_input_container_aborted(self, message: InputContainer.Aborted):
        self.target_process.abort_input()
    
    #---------
        
    def print_log(self, *texts):
        text =' '.join(map(str, texts))
        self.logger_screen.print(text)
    
    def clear_log(self):
        self.logger_screen.logger.clear()
    
    def clear_input(self):
        self.main_screen.input_container.hide()
        self.main_screen.input_container.clear()
    
    def alert(self, text, prompt='Alert'):
        self.alert_screen.set(prompt, text)
        self.push_screen(self.alert_screen)
        press('tab')
        
    def open_input(self):
        self.main_screen.input_container.show()
    
    async def set_input(self, input_request:InputRequest):
        input_container:InputContainer = self.main_screen.input_container
        
        input_container.prompt.value = input_request.prompt
        input_container.help_doc.value = input_request.desc
        input_container.input_box.placeholder = input_request.hint
        pass
        
if __name__ == '__main__':
    app = TUIApp()
    app.run()    