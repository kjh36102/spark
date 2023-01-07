from textual.app import App, ComposeResult, events
from textual.widgets import ListView, ListItem, Label, Footer
from textual.reactive import reactive
from textual.binding import Binding
from rich.console import RenderableType
import textwrap

SYMBOL_UNCHECK = '[ ]'
SYMBOL_CHECK = '[+]'

class ReactiveLabel(Label):
    text = reactive('')

    def __init__(self, renderable: RenderableType = "", *, expand: bool = False, shrink: bool = False, markup: bool = True, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(renderable, expand=expand, shrink=shrink, markup=markup, name=name, id=id, classes=classes)

        self.text = self.renderable
    
    def set_text(self, text):
        self.text = text


class CheckableListItem(ListItem):
    check_box = reactive('[ ]')

    def __init__(self, str, checked=False, show_checkbox=True) -> None:
        super().__init__()

        self.str = str
        self.checked = checked
        self.show_checkbox = show_checkbox

        if checked: self.check_box = SYMBOL_CHECK

    def render(self) -> RenderableType:
        if self.show_checkbox: return f' {self.check_box}  {self.str}'
        else: return f' {self.str}'
        


class Prompt(Label):
    text = reactive('')

    def __init__(self, text, classes=None) -> None:
        super().__init__(classes=classes)

        self.change_text(text)

    def change_text(self, text):
        self.text = text

    def render(self) -> str:
        return self.text

class Selector(App):
    PAGE_MOVE_RATIO = 0.8

    BINDINGS = [
        Binding('w', 'cursor_up', 'up'),
        Binding('s', 'cursor_down', 'down'),
        Binding('ctrl+w', 'cursor_page_up', 'PageUP', priority=True),
        Binding('ctrl+s', 'cursor_page_down', 'PageDown', priority=True),
        Binding('space', 'cursor_select', 'select', priority=True, show=False),
        Binding('enter', 'submit', 'enter', priority=True, show=False),
        ('Space_', '1', 'select'), #dummy
        ('Enter_', '2', 'submit'), #dummy
        Binding('h', 'change_control_target', 'toggle help'),
    ]

    CSS=\
'''
.prompt {
    width: 100%;
    background: $accent-darken-3;
    text-style: bold;
}
'''

    def __init__(self, prompt='Select what you want.', help_prompt='Do you need help?', item_list=None, multi_select=False, help_text='', show_help=False):
        super().__init__()

        self.help_text = help_text
        self.prompt_text = prompt
        self.help_prompt_text = help_prompt
        self.item_list = item_list
        self.multi_select = multi_select
        self.show_help = show_help

        self.prompt = Prompt(' ' + prompt, classes='prompt')

        self.help_area = ListView()
        self.list = ListView()

        self.selected_items = {}

        self.control_target = self.list

        self.current_app_size = self.size

        if self.multi_select: self.wrap_indent = 6
        else: self.wrap_indent = 3

    def compose(self) -> ComposeResult:

        self.build_item()

        self.build_help()

        if not self.show_help: self.help_area.styles.height = 0

        yield self.prompt
        yield self.help_area
        yield self.list
        yield Footer()

    def on_ready(self):
        self.current_app_width = self.size

    def build_help(self):
        help_splitted = self.help_text.split('\n')
        for chunk in help_splitted:
            chunk_splitted = textwrap.fill(chunk, self.size.width - 5).split('\n')

            for line in chunk_splitted:
                self.help_area.append(ListItem(Label(' ' + line)))
        
    def build_item(self):
        
        def convert(str):
            width = self.size.width - self.wrap_indent - 3
            split_width = width - 2

            first_line = str[:width]
            after_chunk = str[width:]

            seperator = '\n' + (' ' * self.wrap_indent)

            after_chunk = seperator.join([after_chunk[i:i+split_width] for i in range(0, len(after_chunk), split_width)])

            return first_line + (seperator if len(after_chunk) != 0 else '') + after_chunk


        for item in self.item_list:
            self.list.append(CheckableListItem(convert(item), show_checkbox=self.multi_select))

    def on_mount(self):
        self.set_focus(self.list)

    def action_cursor_up(self):
        self.control_target.action_cursor_up()

    def action_cursor_down(self):
        self.control_target.action_cursor_down()
    
    def action_cursor_page_up(self):
        for _ in range(int(self.control_target.size.height * self.PAGE_MOVE_RATIO)):
            self.control_target.action_cursor_up()

    def action_cursor_page_down(self):
        for _ in range(int(self.control_target.size.height * self.PAGE_MOVE_RATIO)):
            self.control_target.action_cursor_down()

    def action_cursor_select(self):
        if self.control_target is self.list:
            self.control_target.action_select_cursor()

    def action_submit(self):
        if self.control_target is self.list:
            if len(self.selected_items) > 0: self.exit(self.selected_items)

    def action_change_control_target(self):
        if self.show_help:
            self.control_target = self.list
            self.show_help = False

            self.list.clear()
            self.build_item()

            self.help_area.styles.height = 0
            self.list.styles.height = self.size.height - 2
            self.prompt.change_text(self.prompt_text)
        else:
            self.control_target = self.help_area
            self.show_help = True

            self.help_area.clear()
            self.build_help()

            self.help_area.styles.height = self.size.height - 2
            self.list.styles.height = 0
            self.prompt.change_text(self.help_prompt_text)


    def on_list_view_selected(self, event: ListView.Selected):
        if self.multi_select:
            if event.item.checked == False: 
                event.item.check_box = SYMBOL_CHECK
                event.item.checked = True

                self.selected_items[self.list.index] = self.item_list[self.list.index]
            else: 
                event.item.check_box = SYMBOL_UNCHECK
                event.item.checked = False

                self.selected_items.pop(self.list.index)
        else:
            self.exit((self.list.index, self.item_list[self.list.index]))
    
    async def _on_resize(self, event: events.Resize) -> None:

        if self.current_app_size.width != event.size.width:
            if self.show_help:
                self.help_area.clear()
                self.build_help()
            else:
                self.list.clear()
                self.build_item()

        self.control_target.styles.height = self.size.height - 2

        self.current_app_size = event.size

        return await super()._on_resize(event)

# my_help=\
# '''Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.
# Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section 1.10.32.
# Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.
# Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section 1.10.32.
# '''

# if __name__ == "__main__":
#     app = Selector(item_list=[f'abcdefghijklmnop1abcdefghijklmnop2abcdefghijklmnop3abcdefghijklmnop4abcdefghijklmnop5abcdefghijklmnop6abcdefghijklmnop7abcdefghijklmnop8abcdefghijklmnop9abcdefghijklmnop{num}' for num in range(100)], multi_select=True, help_text=my_help)
#     res = app.run()

#     print('result:', res)
