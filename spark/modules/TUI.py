from textual.app import App, ComposeResult, events
from textual.widgets import ListView, ListItem, Label, Footer, Header, TextLog, Input
from textual.reactive import reactive
from textual.binding import Binding
from rich.console import RenderableType
from textual.screen import Screen
from textual.containers import Container
import textwrap

class _CheckableListItem(ListItem):
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
        
class _ReactiveLabel(Label):
    text = reactive('')

    def __init__(self, text, renderable: RenderableType = "", *, expand: bool = False, shrink: bool = False, markup: bool = True, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(renderable, expand=expand, shrink=shrink, markup=markup, name=name, id=id, classes=classes)
        self.text = text
        self.styles.background = '#0053aa'
        self.styles.width = '100%'
        self.styles.text_style = 'bold'

    def render(self) -> str:
        return '  ' + self.text


class _TUIBaseScreen(App):

    BINDINGS = [
        Binding('escape', 'escape', 'back', priority=True),
        Binding('ctrl+n', 'open_input_box', 'open input', priority=True),
        Binding('ctrl+x', 'clear_input_box', 'clear input', priority=True),
        Binding('enter', 'enter', 'submit', key_display='Enter', priority=True, show=False),
    ]

    def __init__(self, 
    prompt_text='prompt_text', 
     prompt_show=True, contents=[Label('no content'),], 
    name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name, id, classes)

        self.contents = contents
        self.prompt_text = prompt_text
        self.prompt = _ReactiveLabel(prompt_text, classes='prompt')
        self.container = Container(*self.contents)
        self.input_box = Input(placeholder='Now you entered in input mode.')

        self.show_input_box = False
        self.input_box.styles.display = 'none'
        self.submited_input = ''
        self.last_submitted_input = ''
        self.submitted_callback = lambda x: x
        self.last_submitted_callback = lambda x: x
        self.submitted_callback_args = ()
        self.select_callback = lambda x: x
        self.select_callback_args = ()

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
            self.last_submitted_input = self.submited_input
            self.close_input_box()

            self.submitted_callback(self, *self.submitted_callback_args)
            self.last_submitted_callback = self.submitted_callback


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
        self.app.set_focus(self.input_box)
        self.show_input_box = True

    def close_input_box(self, clear=False):
        self.container.styles.height = self.app.size.height - 3

        self.input_box.styles.display = 'none'
        self.app.set_focus(self.container)
        self.show_input_box = False

        if clear: self.input_box.value = ''

    def request_input(self, msg, callback=None, callback_args=()):
        if self.show_input_box == False:

            if self.last_submitted_callback.__code__ != callback.__code__:
                self.input_box.value = ''
            else:
                self.input_box.value = self.last_submitted_input

            self.input_box.placeholder = msg
            self.open_input_box()

            self.submitted_callback = callback
            self.submitted_callback_args = callback_args

    def get_input(self):
        return self.submited_input

    def set_select_callback(self, callback, args=()):
        self.select_callback = callback
        self.select_callback_args = args
    

class TUIScreen(_TUIBaseScreen):
    BINDINGS = [
        Binding('ctrl+y', 'open_help', 'help', priority=True),

        Binding('up', 'cursor_up', '', show=False, priority=True),
        Binding('down', 'cursor_down', '', show=False, priority=True),
        Binding('pageup', 'cursor_move_page("up")', '', show=False, priority=True),
        Binding('pagedown', 'cursor_move_page("down")', '', show=False, priority=True),

        # Binding('w', 'cursor_up', '', show=False, priority=False),
        # Binding('s', 'cursor_down', '', show=False, priority=False),
        # Binding('ctrl+w', 'cursor_move_page("up")', '', show=False, priority=False),
        # Binding('ctrl+s', 'cursor_move_page("down")', '', show=False, priority=False),

        Binding('space', 'space', 'select', key_display='SPACE'),
    ]

    PAGE_UDOWN_RATIO = 0.8

    def __init__(self, contents, help_doc, multi_select=False, prompt_text='prompt_text', help_title='Do you need help?', prompt_show=True, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        self.multi_select = multi_select

        if self.multi_select: 
            self.wrap_indent = 6
            self.selected_items = {}
        else: 
            self.wrap_indent = 3
            self.selected_items = None

        self.item_list = contents
        self.list = ListView()

        self.list.can_focus = False

        self.help_title = help_title
        self.help_doc = help_doc
        self.show_help_doc = False
        self.help_doc_list = ListView()
        self.help_doc_list.can_focus = False

        contents = [self.list, self.help_doc_list]

        self.control_target = self.list

        super().__init__(prompt_text, prompt_show, contents, name, id, classes)

        self.current_app_size = self.size
        self.list_last_cursor = 0
        self.help_last_cursor = 0

        # self.list.styles.height = self.container.size.height

    def on_list_view_highlighted(self, message: ListView.Highlighted):
        if self.show_help_doc:
            self.help_last_cursor = self.help_doc_list.index
        else:
            self.list_last_cursor = self.list.index

    def compose(self) -> ComposeResult:
        return super().compose()

    def on_ready(self) -> None:
        self.refresh_list()
        self.refresh_help()
        self.close_help_doc()
        self.set_focus(self.list)

    def action_cursor_up(self):
        self.control_target.action_cursor_up()
    
    def action_cursor_down(self):
        self.control_target.action_cursor_down()

    def action_cursor_move_page(self, directon):
        for _ in range(int(self.container.size.height * self.PAGE_UDOWN_RATIO)):
            self.control_target.action_cursor_up() if directon == 'up' else self.control_target.action_cursor_down()

    def action_open_help(self):
        self.open_help_doc()

    def action_space(self):
        if self.show_help_doc: return

        self.list.action_select_cursor()

    def action_enter(self):
        if self.multi_select and len(self.selected_items) > 0:
            self.select_callback(self, *self.select_callback_args)
            # self.exit(self.selected_items)
            # self.app.pop_screen()
            # self.pop_callback(*self.pop_callback_args)
            # return self.selected_items

        return super().action_enter()

    def action_escape(self):
        if self.show_help_doc and not self.show_input_box:
            self.close_help_doc()

        return super().action_escape()

    def on_list_view_selected(self, event: ListView.Selected):
        if self.show_help_doc: return
        
        if self.multi_select:
            if event.item.checked == False: 
                event.item.check_box = _CheckableListItem.SYMBOL_CHECK
                event.item.checked = True

                self.selected_items[self.list.index] = self.item_list[self.list.index]
            else: 
                event.item.check_box = _CheckableListItem.SYMBOL_UNCHECK
                event.item.checked = False

                self.selected_items.pop(self.list.index)
        else:
            self.selected_items = (self.list.index, self.item_list[self.list.index])
            self.select_callback(self, *self.select_callback_args)
            # self.exit(self.selected_items)
            # self.app.pop_screen()
            # self.pop_callback(*self.pop_callback_args)
            # return self.selected_items

    async def _on_resize(self, event: events.Resize) -> None:
        await super()._on_resize(event)

        if self.current_app_size.width != event.size.width:
            if self.show_help_doc:
                self.refresh_help()
            else:
                self.refresh_list()

        self.control_target.styles.height = self.container.size.height
        self.current_app_size = event.size

    def build_item(self):

        def convert(str):
            width = self.app.size.width - self.wrap_indent - 3
            split_width = width - 2

            first_line = str[:width]
            after_chunk = str[width:]

            seperator = '\n' + (' ' * self.wrap_indent)

            after_chunk = seperator.join([after_chunk[i:i+split_width] for i in range(0, len(after_chunk), split_width)])

            return first_line + (seperator if len(after_chunk) != 0 else '') + after_chunk


        for item in self.item_list:
            self.list.append(_CheckableListItem(convert(item), show_checkbox=self.multi_select))

    def build_help(self):
        help_splitted = self.help_doc.split('\n')
        for chunk in help_splitted:
            chunk_splitted = textwrap.fill(chunk, self.app.size.width - 5).split('\n')

            for line in chunk_splitted:
                self.help_doc_list.append(ListItem(Label(' ' + line)))

    def refresh_list(self):
        saved_cursor = self.list_last_cursor
        self.list.clear()
        self.build_item()
        self.list.index = saved_cursor

    def refresh_help(self):
        saved_cursor = self.help_last_cursor
        self.help_doc_list.clear()
        self.build_help()
        self.help_doc_list.index = saved_cursor

    def refresh_all(self):
        self.refresh_list()
        self.refresh_help()

    def open_help_doc(self):
        self.prompt.text = self.help_title
        self.control_target = self.help_doc_list

        self.refresh_help()

        self.help_doc_list.styles.height = self.container.size.height
        self.list.styles.height = 0

        self.show_help_doc = True

    def close_help_doc(self):
        self.prompt.text = self.prompt_text
        self.control_target = self.list

        self.refresh_list()

        self.help_doc_list.styles.height = 0
        self.list.styles.height = self.container.size.height

        self.show_help_doc = False

            
# class InputApp(Screen):
#     """App to display key events."""

#     def compose(self) -> ComposeResult:
#         yield TextLog()

#     def on_key(self, event: events.Key) -> None:
#         self.query_one(TextLog).write(event)


# help_str = '''\
# Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.
# Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section 1.10.32.
# Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.
# Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section 1.10.32.\
# '''
# item_list = [f'abcdefghijklmnop1abcdefghijklmnop2abcdefghijklmnop3abcdefghijklmnop4abcdefghijklmnop5abcdefghijklmnop6abcdefghijklmnop7abcdefghijklmnop8abcdefghijklmnop9abcdefghijklmnop{num}' for num in range(100)]

# class BSODApp(App):
#     BINDINGS = [
#         # ('ctrl+b', 'push_screen("bb")', 'key log')
#     ]

#     def __init__(self):
#         super().__init__()

#         # self.list = [
#         #     (f'hi{i}')for i in range(100)
#         # ]

#     def on_mount(self) -> None:
#         # self.install_screen(TUIBaseScreen(), name="aa")
#         # self.install_screen(InputApp(), name="bb")
#         # global help_str
#         # global item_list

#         self.install_screen(TUIScreen(contents=item_list, help_doc=help_str, multi_select=True), name='aa')

#         self.install_screen(TUIBaseScreen(contents=[
#             ListView(
#                 ListItem(Label('hi1')),
#                 ListItem(Label('hi2')),
#                 ListItem(Label('hi3')),
#             ),
#             ListView(
#                 ListItem(Label('greet1')),
#                 ListItem(Label('greet2')),
#                 ListItem(Label('greet3')),
#             )
#         ]), name='bb')

#         self.push_screen('aa')


# if __name__ == "__main__":
#     app = BSODApp()
#     app.run()


