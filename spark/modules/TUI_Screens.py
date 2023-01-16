from textual.app import events
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, TextLog, Button
from textual.containers import Container, Grid
from TUI_Widgets import Prompt, ReactiveLabel, LoadingBox, InputContainer, ListContainer


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
        
        self.prompt = Prompt('Log')
        self.logger = TextLog(max_lines=200, wrap=True)
        self.loading_box = LoadingBox()
        self.escape_lock = False
        
    def compose(self):
        yield self.prompt
        yield self.logger
        yield self.loading_box
        yield Footer()
        
    def on_mount(self):
        self.close_loading_box()
        
    async def _on_idle(self, event: events.Idle) -> None:
        
        if self.loading_box.show_state:
            self.logger.styles.height = self.app.size.height - 3
        else:
            self.logger.styles.height = self.app.size.height - 2
        
        return await super()._on_idle(event)
        
    BINDINGS = [
        Binding('ctrl+a', 'clear_up', 'clear'),
        Binding('escape', 'pop_screen()', 'back'),
        Binding('up', 'scroll_up', 'up'),
        Binding('down', 'scroll_down', 'down'),
        Binding('pageup', 'scroll_page_up', 'pageup'),
        Binding('pagedown', 'scroll_page_down', 'pagedown'),
        Binding('home', 'scroll_home', 'home'),
        Binding('end', 'scroll_end', 'end'),
    ]
    
    def action_pop_screen(self):
        if self.escape_lock: return
        
        self.app.pop_screen()
            
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
    
    def action_clear_up(self):
        self.logger.clear()
        
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