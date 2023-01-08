from textual.app import App, ComposeResult, events
from textual.widgets import ListView, ListItem, Label, Footer, Header, TextLog, Input
from textual.reactive import reactive
from textual.binding import Binding
from rich.console import RenderableType
from textual.screen import Screen
from textual.containers import Container


class CheckableListItem(ListItem):
    SYMBOL_UNCHECK = '[ ]'
    SYMBOL_CHECK = '[+]'
    check_box = reactive('[ ]')

    def __init__(self, str, checked=False, show_checkbox=True) -> None:
        super().__init__()

        self.str = str
        self.checked = checked
        self.show_checkbox = show_checkbox

        if checked: self.check_box = self.SYMBOL_CHECK

    def render(self) -> RenderableType:
        if self.show_checkbox: return f' {self.check_box}  {self.str}'
        else: return f' {self.str}'
        

#TODO input box에 모두 지우는 기능 추가하기
class ReactiveLabel(Label):
    text = reactive('')

    def __init__(self, text, renderable: RenderableType = "", *, expand: bool = False, shrink: bool = False, markup: bool = True, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(renderable, expand=expand, shrink=shrink, markup=markup, name=name, id=id, classes=classes)
        self.text = text
        self.styles.background = '#0178d4'
        self.styles.width = '100%'
        self.styles.text_style = 'bold'

    def render(self) -> str:
        return ' ' + self.text


class TUIBaseScreen(Screen):

    BINDINGS = [
        Binding('escape', 'escape', 'escape', priority=True),
        Binding('h', 'open_help_screen', 'help', priority=True),
        Binding('ctrl+n', 'open_input_box', 'open input', priority=True),
        Binding('ctrl+x', 'clear_input_box', 'clear input', priority=True),
        Binding('enter', 'enter', 'submit', key_display='Enter', priority=True, show=False),
        # Binding('ctrl+w', 'request_input', 'request', priority=True),
        # Binding('ctrl+a', 'check_input', 'check input', priority=True),
    ]

    def __init__(self, 
    prompt_text='prompt_text', prompt_show=True, contents=[Label('no content'),],
    name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name, id, classes)

        self.contents = contents
        self.prompt = ReactiveLabel(prompt_text, classes='prompt')
        self.container = Container(*self.contents)
        self.input_box = Input(placeholder='Now you entered in input mode.')

        self.show_input_box = False
        self.input_box.styles.display = 'none'
        self.submited_input = ''
        self.submited_flag = False

        if not prompt_show: self.prompt.styles.height = 0

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield self.prompt
        yield self.container
        yield self.input_box
        yield Footer()

    def action_escape(self):
        if self.show_input_box == True:
            self.close_input_box()
    
    def action_enter(self):
        if self.show_input_box == True:
            self.submited_input = self.input_box.value
            self.submited_flag = True
            self.close_input_box(clear=True)

    def action_open_input_box(self):
        if self.show_input_box == False:
            self.open_input_box()

    def action_clear_input_box(self):
        if self.show_input_box == True:
            self.input_box.value = ''

    async def _on_resize(self, event: events.Resize) -> None:
        if self.show_input_box:
            self.container.styles.height = self.app.size.height - 6
        else: 
            self.container.styles.height = self.app.size.height - 3
        return await super()._on_resize(event)
    
    def open_input_box(self):
        self.container.styles.height = self.container.size.height - 3

        self.input_box.styles.display = 'block'
        app.set_focus(self.input_box)
        self.show_input_box = True

    def close_input_box(self, clear=False):
        self.container.styles.height = self.app.size.height - 3

        self.input_box.styles.display = 'none'
        self.app.set_focus(self.container)
        self.show_input_box = False

        if clear: self.input_box.value = ''

    def request_input(self, msg):
        if self.show_input_box == False:
            self.input_box.value = ''
            self.input_box.placeholder = msg
            self.open_input_box()

    def get_input(self):
        if self.submited_flag:
            self.submited_flag = False
            return self.submited_input
        return None
    
    # def action_request_input(self):
    #     self.request_input(msg='hello')
    
    # def action_check_input(self):
    #     text = self.get_input()
    #     if text != None:
    #         self.prompt.text = text


class Selector(TUIBaseScreen):
    BINDINGS = [
        Binding('up', 'cursor_up', '', show=False),
        Binding('down', 'cursor_down', '', show=False),
        Binding('pageup', 'cursor_move_page("up")', '', show=False),
        Binding('pagedown', 'cursor_move_page("down")', '', show=False),
        Binding('space', 'space', 'select', key_display='SPACE'),
    ]

    PAGE_UDOWN_RATIO = 0.8

    def __init__(self, contents, multi_select=False, prompt_text='prompt_text', prompt_show=True, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:

        self.multi_select = multi_select
        self.item_list = contents
        self.list = ListView(*[(CheckableListItem(str=line, show_checkbox=multi_select))for line in contents])
        contents = [self.list]

        super().__init__(prompt_text, prompt_show, contents, name, id, classes)

        if multi_select:
            self.selected_items = {}
        else:
            self.selected_items = None

    def action_cursor_up(self):
        self.list.action_cursor_up()
    
    def action_cursor_down(self):
        self.list.action_cursor_down()

    def action_cursor_move_page(self, directon):
        for _ in range(int(self.list.size.height * self.PAGE_UDOWN_RATIO)):
            self.list.action_cursor_up() if directon == 'up' else self.list.action_cursor_down()

    def action_space(self):
        self.list.action_select_cursor()

    def action_enter(self):
        if self.multi_select and len(self.selected_items) > 0:
            self.app.pop_screen()

        return super().action_enter()

    def on_list_view_selected(self, event: ListView.Selected):
        if self.multi_select:
            if event.item.checked == False: 
                event.item.check_box = CheckableListItem.SYMBOL_CHECK
                event.item.checked = True

                self.selected_items[self.list.index] = self.item_list[self.list.index]
            else: 
                event.item.check_box = CheckableListItem.SYMBOL_UNCHECK
                event.item.checked = False

                self.selected_items.pop(self.list.index)
        else:
            self.selected_items = (self.list.index, self.item_list[self.list.index])
            self.app.pop_screen()

class HelpScreen(TUIBaseScreen):
    BINDINGS = [
        Binding('escape', 'close_help_screen', 'escape')
    ]

    def __init__(self, help_str, prompt_text='prompt_text', prompt_show=True, contents=[Label('no content')], name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(prompt_text, prompt_show, contents, name, id, classes)

        self.help_str = help_str

    def compose(self) -> ComposeResult:
        yield Label(self.help_str)


class InputApp(Screen):
    """App to display key events."""

    def compose(self) -> ComposeResult:
        yield TextLog()

    def on_key(self, event: events.Key) -> None:
        self.query_one(TextLog).write(event)

class BSODApp(App):
    BINDINGS = [
        # ('ctrl+b', 'push_screen("bb")', 'key log')
    ]

    def __init__(self):
        super().__init__()

        self.list = [
            (f'hi{i}')for i in range(100)
        ]

    def on_mount(self) -> None:
        # self.install_screen(TUIBaseScreen(), name="aa")
        self.install_screen(InputApp(), name="bb")
        self.install_screen(Selector(contents=self.list, multi_select=True), name='aa')

        self.push_screen('aa')


if __name__ == "__main__":
    app = BSODApp()
    app.run()


