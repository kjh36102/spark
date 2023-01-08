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
        Binding('ctrl+d', 'open_input_box', 'open input', priority=True),
        Binding('escape', 'escape', 'escape', priority=True),
    ]

    def __init__(self, 
    prompt_text='prompt_text', prompt_show=True, contents=[Label('no content'),],
    name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name, id, classes)

        self.contents = contents
        self.prompt = ReactiveLabel(prompt_text, classes='prompt')
        self.container = Container(*self.contents)
        self.input_box = Input(placeholder='Press tab to focus here')

        self.show_input_box = False
        self.input_box.styles.display = 'none'

        if not prompt_show: self.prompt.styles.height = 0

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield self.prompt
        yield self.container
        yield self.input_box
        yield Footer()

    def action_open_input_box(self):
        if self.show_input_box == False:
            self.container.styles.height = self.container.size.height - 3

            self.input_box.styles.display = 'block'
            app.set_focus(self.input_box)
            self.show_input_box = True

    def action_escape(self):
        if self.show_input_box == True:
            self.container.styles.height = self.app.size.height - 3

            self.input_box.styles.display = 'none'
            # app.set_focus(self.app)
            self.show_input_box = False
    
    # def key_i(self):
    #     if self.show_input_box == True:
    #         self.input_box.insert_text_at_cursor('i')

    # async def _on_key(self, event: events.Key) -> None:
    #     if self.show_input_box == True:
    #         if event.character == 'i': self.input_box.insert_text_at_cursor('i')
    #         return await super()._on_key(event)
    
    async def _on_resize(self, event: events.Resize) -> None:
        if self.show_input_box:
            self.container.styles.height = self.app.size.height - 6
            pass
        else:
            self.container.styles.height = self.app.size.height - 3
            pass
        return await super()._on_resize(event)


class InputApp(Screen):
    """App to display key events."""

    def compose(self) -> ComposeResult:
        yield TextLog()

    def on_key(self, event: events.Key) -> None:
        self.query_one(TextLog).write(event)

class BSODApp(App):
    BINDINGS = [
    ]

    def __init__(self):
        super().__init__()

        self.list = [
            ListView(
                *list(( ListItem(Label(f'hi{i}')) )for i in range(20))
            )
        ]

    def on_mount(self) -> None:
        self.install_screen(TUIBaseScreen(), name="aa")
        self.install_screen(InputApp(), name="bb")

        self.push_screen('aa')


if __name__ == "__main__":
    app = BSODApp()
    app.run()


