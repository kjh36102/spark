from textual.app import App, ComposeResult
from textual.widgets import ListView, ListItem, Label, Footer
from textual import events


class SelectOne(App):
    def __init__(self, item_list=None):
        super().__init__()

        self.item_list = item_list
        self.list = ListView()
        self.select_item = None

    # CSS_PATH = "stopwatch.css"

    BINDINGS = [
        ('w', 'cursor_up', 'up'),
        ('s', 'cursor_down', 'down'),
        ('a', 'select_item', 'select'),
    ]

    def run(self):
        super().run()
        return self.select_item

    def compose(self) -> ComposeResult:
        # list = ListView()
        for item in self.item_list:
            self.list.append(ListItem(Label(item)))
        
        yield self.list
        yield Footer()

    def action_cursor_up(self):
        self.list.action_cursor_up()

    def action_cursor_down(self):
        self.list.action_cursor_down()

    def action_select_item(self):
        print(self.list.index)
    
    def on_item_selected(self, event: ListView.Selected):
        # self.select_item = event.item
        super().exit(event.item.id)


    # def action_focus_previous(self) -> None:
    #     self.list.action
    #     return super().action_focus_previous()

    # def action_focus_next(self) -> None:
    #     return super().action_focus_next()


if __name__ == "__main__":
    app = SelectOne(item_list=['hi1', 'hi2', 'hi3'])
    res = app.run()

    print('result:', res)
