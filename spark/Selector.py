from textual.app import App, ComposeResult
from textual.widgets import ListView, ListItem, Label, Footer
from textual.reactive import reactive
from textual.binding import Binding

SYMBOL_UNCHECK = '[ ]'
SYMBOL_CHECK = '[+]'

class CheckableListItem(ListItem):
    check_box = reactive('[ ]')

    def __init__(self, str, checked=False) -> None:
        super().__init__()

        self.str = str
        self.checked = checked

        if checked: self.check_box = SYMBOL_CHECK

    def render(self) -> str:
        return f' {self.check_box}  {self.str}'

class Selector(App):
    PAGE_MOVE_RATIO = 0.8

    BINDINGS = [
        Binding('w', 'cursor_up', 'up', show=False),
        Binding('s', 'cursor_down', 'down', show=False),
        Binding('ctrl+w', 'cursor_page_up', 'page_up', show=False, priority=True),
        Binding('ctrl+s', 'cursor_page_down', 'page_down', show=False, priority=True),
        Binding('space', 'cursor_select', 'select', show=False),
        Binding('enter', 'submit', 'submit', show=False, priority=True),

        #dummies
        ('_w_', '1', 'up'),
        ('_s_', '2', 'down'),
        ('_ctrl+w_', '3', 'page_up'),
        ('_ctrl+s_', '4', 'page_down'),
        ('_Space_', '5', 'select'), 
        ('_Enter_', '6', 'submit'), 
    ]

    def __init__(self, prompt='', item_list=None, multi_select=False):
        super().__init__()

        self.prompt = prompt
        self.item_list = item_list
        self.list = ListView()

        self.multi_select = multi_select
        self.selected_items = {}

    def compose(self) -> ComposeResult:

        if self.multi_select:
            for item in self.item_list:
                self.list.append(CheckableListItem(item,))
        else:
            for item in self.item_list:
                self.list.append(ListItem(Label(' ' + item)))

        yield Label(self.prompt)
        yield self.list
        yield Footer()

    def on_mount(self):
        self.set_focus(self.list)

    def action_cursor_up(self):
        self.list.action_cursor_up()

    def action_cursor_down(self):
        self.list.action_cursor_down()
    
    def action_cursor_page_up(self):
        for _ in range(int(self.size.height * self.PAGE_MOVE_RATIO)):
            self.list.action_cursor_up()

    def action_cursor_page_down(self):
        for _ in range(int(self.size.height * self.PAGE_MOVE_RATIO)):
            self.list.action_cursor_down()

    def action_cursor_select(self):
        self.list.action_select_cursor()

    def action_submit(self):
        if len(self.selected_items) > 0: self.exit(self.selected_items)

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

# if __name__ == "__main__":
#     app = Selector(prompt='Select what you want.', item_list=[f'hi{num}' for num in range(100)], multi_select=True)
#     res = app.run()

#     print('result:', res)
