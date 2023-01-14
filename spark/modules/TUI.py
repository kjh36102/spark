from textual.app import App, events
from textual.binding import Binding
from textual.screen import Screen
from textual.containers import Container
from textual.widgets import Label, Footer, ListView, TextLog, Input, Button
from textual.containers import Grid

from TUI_events import *
from TUI_DAO import *
from TUI_Widgets import ReactiveLabel, Prompt, CheckableListItem


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
    
    def action_close_container(self):
        self.hide()
    
    def action_expand_input_help(self):
        if self.expand_state == False:
            self.expand_state = True
        else: self.expand_state = False
            
        self.set(self.prompt_origin, self.help_doc_origin, self.input_box.placeholder, preserve_value=True)
        
    async def action_submit_input(self):
        await self.emit(InputSubmit(self, self.input_box.value))
        self.input_box.value = ''
        
    async def action_abort_input(self):
        await self.emit(InputAborted(self))
        
    def __set(self, prompt, help_doc, hint, preserve_value=False):
        new_prompt = ReactiveLabel(prompt, indent=1, bold=True)
        new_help_doc = ReactiveLabel(help_doc, indent=3)
        self.input_box.placeholder = hint
      
        self.prompt.remove()
        self.help_doc.remove()
        
        self.prompt_container.mount(new_prompt)
        self.help_doc_container.mount(new_help_doc)
        
        self.prompt = new_prompt
        self.help_doc = new_help_doc
        
        if help_doc == '': self.help_doc.styles.display = 'none'
        if not preserve_value: self.input_box.value = ''
        
    def set(self, prompt, help_doc='', hint='', preserve_value=False):
        self.prompt_origin = prompt
        self.help_doc_origin = help_doc
            
        self.__set(self.prompt_origin, self.help_doc_origin, hint, preserve_value)

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
    def __init__(self, list_view = ListView(Label('Empty list')), multi_select=False) -> None:
        self.list = list_view
        super().__init__(self.list)
        self.multi_select = multi_select
    
    class Selected(Message):
        def __init__(self, sender: MessageTarget, index, item) -> None:
            super().__init__(sender)
            self.index = index
            self.item = item
    
    class Pop(Message):
        def __init__(self, sender: MessageTarget) -> None:
            super().__init__(sender)
        
    BINDINGS = [
        Binding('space', 'select_item', 'select', key_display='SPACE'),
        Binding('escape', 'press_escape', 'back'),
        Binding('pageup', 'scroll_page_up', 'pageup', priority=True),
        Binding('pagedown', 'scroll_page_down', 'pagedown', priority=True),
        Binding('home', 'scroll_home', 'home', priority=True),
        Binding('end', 'scroll_end', 'end', priority=True),
    ]
        
    async def action_select_item(self):
        idx = self.list.index
        item:CheckableListItem = self.list.children[idx]
        await self.emit(self.Selected(self, idx, item))
        
    async def action_press_escape(self):
        await self.emit(self.Pop(self.app))
        pass
        
    def action_scroll_home(self):
        self.list.index = 0
        
    def action_scroll_end(self):
        self.list.index = len(self.list.children) - 1
        
    def action_scroll_page_up(self):
        unit = int((self.app.size.height - 2) * 0.8)
        self.list.index -= unit
        
    def action_scroll_page_down(self):
        unit = int((self.app.size.height - 2) * 0.8)
        self.list.index += unit
        

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

class FormContainer(Container):
    def __init__(self, *children):
        super().__init__(*children)
        
        self.styles.width = '100%'
        self.styles.height = self.app.size.height - 2        

class FormScreen(Screen):
    def __init__(self, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name, id, classes)
        
        self.prompt = Prompt('Empty prompt.')
        self.form_container = FormContainer(
            InputContainer()
        )
        
    def compose(self):
        yield self.prompt
        yield self.form_container
        yield Footer()
    

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
        self.scene_stack = []

    def compose(self):
        yield self.prompt
        yield self.contents_container
        yield Footer()
        
    # when user press esc on list
    def on_list_container_pop(self, message: ListContainer.Pop):
        self.pop_scene()
        
    def on_list_container_selected(self, message: ListContainer.Selected):
        message.item.callback(self.app, message.item, *message.item.callback_args)
        
    async def on_idel(self):
        self.list_container.styles.height = ((self.app.size.height - 2) - self.input_container.size.height)
        
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
        
    def _change_scene(self, scene:Scene):
        #change prompts and help doc
        self.prompt.value = scene.main_prompt
        self.app.help_screen.set(scene.help_prompt, scene.help_title, scene.help_doc)
        
        #remove current list
        self.list_container.list.remove()
        
        #build new list
        scene.rebuild_items()   #This is required because widgets that have been removed once cannot be remounted
        self.list_container.list = ListView(*scene.items)
        
        #mount new list
        self.list_container.mount(self.list_container.list)
        
        #set focus to list view
        self.app.set_focus(self.list_container.list)
        
        #restore cursor        
        self.list_container.list.index = scene.current_cursor
        
        #scroll down to previous highlighted item
        self.list_container.list.highlighted_child.scroll_visible(animate=False)
        
    def push_scene(self, scene:Scene):
        try: 
            if self.scene_stack[-1] is scene: return
            
            #save current cursor if there is scene
            self.scene_stack[-1].current_cursor = self.list_container.list.index
            # self.app.print('saving index:', self.scene_stack[-1].current_cursor)
        except IndexError: pass
        
        self._change_scene(scene)
        self.scene_stack.append(scene)
    
    def pop_scene(self):
        if len(self.scene_stack) >= 2:
            self.scene_stack.pop()
            self._change_scene(self.scene_stack[-1])
   

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
                
        self.custom_process = None

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
        pass
    
    #---------
    
    def on_input_submit(self, message: InputSubmit):
        if self.custom_process != None: self.custom_process.response_input(message.value)
    
    def on_input_aborted(self, message: InputAborted):
        if self.custom_process != None: self.custom_process.stop()
        
    def print_log(self, *texts):
        text =' '.join(map(str, texts))
        self.logger_screen.print(text)
    
    def clear_log(self):
        self.logger_screen.logger.clear()
        
    def run_custom_process(self, custom_process):
        self.custom_process = custom_process
        self.custom_process.run()
        
    def alert(self, text, prompt='Alert'):
        self.alert_screen.set(prompt, text)
        self.push_screen(self.alert_screen)
        
    def push_scene(self, scene):
        self.main_screen.push_scene(scene)
        
    def pop_scene(self):
        self.main_screen.pop_scene()
    

if __name__ == '__main__':
    app = TUIApp()
    app.run()    
