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
    SYMBOL_CHECK = '[✔]'
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


class Selector(App):

    BINDINGS = [
        Binding('escape', 'escape', 'back', priority=True),
        Binding('ctrl+n', 'open_input_box', 'open input', priority=True),
        Binding('ctrl+x', 'clear_input_box', 'clear input', priority=True),
        Binding('enter', 'enter', 'submit', key_display='Enter', priority=True, show=False),
        Binding('ctrl+y', 'open_help', 'help', priority=True),
        Binding('up', 'cursor_up', '', show=False, priority=True),
        Binding('down', 'cursor_down', '', show=False, priority=True),
        Binding('pageup', 'cursor_move_page("up")', '', show=False, priority=True),
        Binding('pagedown', 'cursor_move_page("down")', '', show=False, priority=True),
        Binding('space', 'space', 'select', key_display='SPACE'),
    ]

    PAGE_UPDOWN_RATIO = 0.8

    def __init__(
        self, 
        contents=['no contents'], 
        help_doc='no help doc',
        multi_select=False,
        prompt_show=True, 
        contents_prompt='Select what you want.', 
        help_prompt='Do you need help?'
    ):
        super().__init__()

        self.contents = contents
        self.help_doc = help_doc
        self.multi_select = multi_select
        self.prompt_show = prompt_show
        self.contents_prompt = contents_prompt
        self.help_prompt = help_prompt

        self.prompt = _ReactiveLabel(contents_prompt)
        self.contents_listview = ListView()
        self.help_listview = ListView()
        self.container = Container(self.contents_listview, self.help_listview)
        self.input_box = Input()

        self.submitted_input = ''
        self.last_submitted_input = ''

        self.last_submitted_callback = lambda x: x
        self.submitted_callback = lambda x: x
        self.submitted_callback_args = ()

        self.select_callback = lambda x: x
        self.select_callback_args = ()

        self.wrap_indent = 3 if multi_select else 6
        
        self.selected_items = {} if multi_select else None

        self.control_target = self.contents_listview

        self.current_app_size = self.size

        self.contents_last_cursor = 0
        self.help_last_cursor = 0

        self.page_stack = []
        
        #states
        self.state_input_box = False
        self.state_help_doc = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield self.prompt
        yield self.container
        yield self.input_box
        yield Footer()

    def on_mount(self):
        #style
        self.input_box.styles.display = 'none'
        self.help_listview.styles.height = 0

    def on_ready(self):
        #after work
        self.contents_listview.can_focus = False
        self.help_listview.can_focus = False

        self.refresh_list()
        self.refresh_help()
        self.close_help_doc()
        self.set_focus(self.contents_listview)

    def on_list_view_highlighted(self, message: ListView.Highlighted):
        if self.state_help_doc:
            self.help_last_cursor = self.help_listview.index
        else:
            self.contents_last_cursor = self.contents_listview.index

    def on_list_view_selected(self, event: ListView.Selected):
        if self.state_help_doc: return
        
        if self.multi_select:
            if event.item.checked == False: 
                event.item.check_box = _CheckableListItem.SYMBOL_CHECK
                event.item.checked = True

                self.selected_items[self.contents_listview.index] = self.contents[self.contents_listview.index]
            else: 
                event.item.check_box = _CheckableListItem.SYMBOL_UNCHECK
                event.item.checked = False

                self.selected_items.pop(self.contents_listview.index)
        else:
            self.selected_items = (self.contents_listview.index, self.contents[self.contents_listview.index])
            self.select_callback(self, *self.select_callback_args)
            # self.exit(self.selected_items)
            # self.app.pop_screen()
            # self.pop_callback(*self.pop_callback_args)
            # return self.selected_items            

    # def action_escape(self):
    #     if self.state_input_box == True:
    #         self.close_input_box()
    #     else:
    #         self.previous_page()
    
    # def action_enter(self):
    #     if self.state_input_box == True:
    #         self.submited_input = self.input_box.value
    #         self.last_submitted_input = self.submited_input
    #         self.close_input_box()

    #         self.submitted_callback(self, *self.submitted_callback_args)
    #         self.last_submitted_callback = self.submitted_callback
    
    def action_open_input_box(self):
        if self.state_input_box == False:
            self.open_input_box()

    def action_clear_input_box(self):
        if self.state_input_box == True:
            self.input_box.value = ''

    def action_cursor_up(self):
        self.control_target.action_cursor_up()
    
    def action_cursor_down(self):
        self.control_target.action_cursor_down()

    def action_cursor_move_page(self, directon):
        for _ in range(int(self.container.size.height * self.PAGE_UPDOWN_RATIO)):
            self.control_target.action_cursor_up() if directon == 'up' else self.control_target.action_cursor_down()

    def action_open_help(self):
        self.open_help_doc()

    def action_space(self):
        if self.state_help_doc: return

        self.contents_listview.action_select_cursor()

    def action_enter(self):
        if self.state_input_box == True:
            self.submited_input = self.input_box.value
            self.last_submitted_input = self.submited_input
            self.close_input_box()

            self.submitted_callback(self, *self.submitted_callback_args)
            self.last_submitted_callback = self.submitted_callback
            return

        if self.multi_select and len(self.selected_items) > 0:
            self.select_callback(self, *self.select_callback_args)

            # self.exit(self.selected_items)
            # self.app.pop_screen()
            # self.pop_callback(*self.pop_callback_args)
            # return self.selected_items

    def action_escape(self):
        if self.state_input_box == True:
            self.close_input_box()
            return

        if self.state_help_doc and not self.state_input_box:
            self.close_help_doc()
            return
        
        self.previous_page()

    def open_input_box(self):
        self.container.styles.height = self.container.size.height - 3

        self.input_box.styles.display = 'block'
        self.app.set_focus(self.input_box)
        self.state_input_box = True

    def close_input_box(self, clear=False):
        self.container.styles.height = self.app.size.height - 3

        self.input_box.styles.display = 'none'
        self.app.set_focus(self.container)
        self.state_input_box = False

        if clear: self.input_box.value = '' 

    def request_input(self, msg, callback=None, callback_args=()):
        if self.state_input_box == False:

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

    def build_item(self):

        def convert(str):
            width = self.app.size.width - self.wrap_indent - 3
            split_width = width - 2

            first_line = str[:width]
            after_chunk = str[width:]

            seperator = '\n' + (' ' * self.wrap_indent)

            after_chunk = seperator.join([after_chunk[i:i+split_width] for i in range(0, len(after_chunk), split_width)])

            return first_line + (seperator if len(after_chunk) != 0 else '') + after_chunk

        if self.multi_select:
            for idx, item in enumerate(self.contents):
                self.contents_listview.append(
                    _CheckableListItem(convert(item), show_checkbox=True, checked=True if self.selected_items.get(idx) else False)
                )
        else:
            for item in self.contents:
                self.contents_listview.append(_CheckableListItem(convert(item), show_checkbox=False))

    def build_help(self):
        help_splitted = self.help_doc.split('\n')
        for chunk in help_splitted:
            chunk_splitted = textwrap.fill(chunk, self.app.size.width - 5).split('\n')

            for line in chunk_splitted:
                self.help_listview.append(ListItem(Label(' ' + line)))   

    def refresh_list(self):
        self.prompt.text = self.contents_prompt
        saved_cursor = self.contents_last_cursor
        self.contents_listview.clear()
        self.build_item()
        self.contents_listview.index = saved_cursor

    def refresh_help(self):
        self.prompt.text = self.help_prompt
        saved_cursor = self.help_last_cursor
        self.help_listview.clear()
        self.build_help()
        self.help_listview.index = saved_cursor

    def refresh_all(self):
        self.refresh_list()
        self.refresh_help()    

    def open_help_doc(self):
        self.prompt.text = self.help_prompt
        self.control_target = self.help_listview

        self.refresh_help()

        self.help_listview.styles.height = self.container.size.height
        self.contents_listview.styles.height = 0

        self.state_help_doc = True

    def close_help_doc(self):
        self.prompt.text = self.contents_prompt
        self.control_target = self.contents_listview

        self.refresh_list()

        self.help_listview.styles.height = 0
        self.contents_listview.styles.height = self.container.size.height

        self.state_help_doc = False   

    def next_page(self, contents=['no contents'], help='no help', contents_prompt='no contents prompt', help_prompt='no help prompt', funcs=None, callback=None):
        
        

        if funcs != None:
            callback = lambda self: (funcs[self.selected_items[0]](self))
            contents = [func.__name__.replace('_', ' ') for func in funcs]

        self.page_stack.append((self.contents, self.help_doc, self.contents_prompt, self.help_prompt, callback))

        self.contents = contents
        self.help_doc = help
        self.contents_prompt = contents_prompt
        self.help_prompt = help_prompt
        self.refresh_all()

        self.set_select_callback(callback)

        # self.page_stack.append((contents, self.help_doc, self.contents_prompt, self.help_prompt, callback))

        self.prompt.text = str(self.page_stack)

    def previous_page(self):
        if len(self.page_stack) <= 1: return

        previous_scene = self.page_stack.pop()

        contents = previous_scene[0]
        help_doc = previous_scene[1]
        contents_prompt = previous_scene[2]
        help_prompt = previous_scene[3]
        callback = previous_scene[4]
        
        self.contents = contents
        self.help_doc = help_doc
        self.contents_prompt = contents_prompt
        self.help_prompt = help_prompt
        self.refresh_all()

        self.set_select_callback(callback)

        self.prompt.text = str(self.page_stack)

    async def _on_resize(self, event: events.Resize) -> None:
        if self.state_input_box:
            self.container.styles.height = self.app.size.height - 6
        else: 
            self.container.styles.height = self.app.size.height - 3

        if self.current_app_size.width != event.size.width:
            if self.state_help_doc:
                self.refresh_help()
            else:
                self.refresh_list()

        self.control_target.styles.height = self.container.size.height
        self.current_app_size = event.size
        
        return await super()._on_resize(event)

class Page:
    def __init__(self, ) -> None:
        pass


# funcs = [
#     'create_new_post',
#     'synchronize_post',
#     'commit_and_push',
#     'manage_post',
#     'manage_category',
#     'convert_image_url',
#     'revert_image_url',
#     'config_ftp_info',
#     'change_css_theme',
#     'initialize_blog'
# ]

# help ='''\
# create new post - Create new post automatically.
# synchronize post - Synchronize post with FTP server.
# commit & push - commit and push to github.
# manage post - Managing settings about specific post.
# manage category - Managing your categories.
# convert image URL - Change local image URL to embeded URL from FTP server.
# revert image URL -  Change embeded URL to local image URL.
# config FTP info - Config FTP info for using synchronize feature.
# change CSS theme - Change blog css theme.
# initialize blog - After clone from github, must run this once.\
# '''

# app = Selector(contents=funcs, help_doc=help, multi_select=True)
# app.run()