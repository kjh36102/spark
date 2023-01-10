from textual.app import events
from textual.widgets import ListView, ListItem, Label, Footer, Input
from textual.reactive import reactive
from textual.binding import Binding
from textual.screen import Screen
from textual.containers import Container
from textual.scrollbar import ScrollBar

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

    def render(self):
        if self.show_checkbox: return f' {self.check_box}  {self.str}'
        else: return f' >  {self.str}'
        
class ReactiveLabel(Label):
    text = reactive('')

    def __init__(self, text, classes=None) -> None:
        super().__init__(classes=classes)
        self.text = text

        #styles
        self.styles.background = '#0053aa'
        self.styles.width = '100%'
        self.styles.text_style = 'bold'

    def render(self) -> str:
        return '  ' + self.text

class TUIScreen(Screen):
    BINDINGS = [
        Binding('escape', 'escape', 'back', priority=True),
        Binding('ctrl+n', 'toggle_input_box', 'toggle input', priority=True),
        Binding('ctrl+x', 'clear_input_box', 'clear input', priority=True),
        Binding('h', 'toggle_help', 'toggle help', priority=False),
        Binding('g', 'grab_focus', 'grab focus'),
        Binding('G', 'grab_focus(True)', 'grab focus', show=False),
        Binding('r', 'release_focus', 'release focus'),
        Binding('enter', 'enter', 'submit', key_display='Enter', priority=True, show=False),
        Binding('tab', 'focus_next', '', show=False),
        Binding('shift+tab', 'focus_previous', '', show=False),
        Binding('up', 'scroll_up', '', show=False, priority=True),
        Binding('down', 'scroll_down', '', show=False, priority=True),
        Binding('pageup', 'scroll_page_up', '', show=False, priority=True),
        Binding('pagedown', 'scroll_page_down', '', show=False, priority=True),
    ]

    def __init__(self,
            main_contents=[Label('Empty main contents.')],
            help_contents=[Label('Empty help contents.')],
            main_prompt_str='Empty main prompt.', 
            help_prompt_str='Empty help prompt', 
            show_prompt=True, 
        ) -> None:
        super().__init__()

        #initialize
        self.main_contents = main_contents
        self.help_contents = help_contents
        self.main_prompt_str = main_prompt_str
        self.help_prompt_str = help_prompt_str
        self.show_prompt = show_prompt
        
        #elements
        self.prompt_label = ReactiveLabel(self.main_prompt_str, classes='prompt')
        self.main_container = Container(*self.main_contents)
        self.help_container = Container(*self.help_contents)
        self.input_box = Input(placeholder='Empty placeholder')

        #states
        self.state_show_input = False
        self.state_show_help = False
        self.focus_jump_waiting = False

        #variables
        self.container_max_size = (0, 0)
        self.control_target = self.main_container
        self.input_last_focused = None
        self.input_buffer = None
        self.input_getter = lambda x: x
        self.input_getter_args = ()
        self.saved_focus = None

        #hide all
        self.help_container.styles.display = 'none'
        self.input_box.styles.display = 'none'

    def compose(self):
        yield self.prompt_label
        yield self.input_box
        yield self.main_container
        yield self.help_container
        yield Footer()

# events------------------------------------------------------------------------------------------
    def on_ready(self):
        self.action_focus_next()

    async def on_resize(self, event: events.Resize) -> None:
        self.container_max_size = (self.app.size.width - 1, self.app.size.height - 2)
        return await super()._on_resize(event)
# ------------------------------------------------------------------------------------------------

# actions-----------------------------------------------------------------------------------------
    def action_enter(self):
        if self.state_show_input:
            self.input_buffer = self.input_box.value
            self.switch_input_box(close=True, clear=True)
            self.__run_input_getter()
            return True
        return False

    def action_toggle_input_box(self):
        self.switch_input_box()

    def action_clear_input_box(self):
        if self.state_show_input:
            self.input_box.value = ''

    def action_toggle_help(self):
        self.switch_container()
    
    #scrollings
    def action_scroll_up(self) -> None:
        if type(self.focused) == ListView:
            self.focused.action_cursor_up()
        else:
            self.control_target.scroll_up()
            return super().action_scroll_up()

    def action_scroll_down(self) -> None:
        if type(self.focused) == ListView:
            self.focused.action_cursor_down()
        else:
            self.control_target.scroll_down()
            return super().action_scroll_down()

    def action_scroll_page_up(self):
        unit = int((self.app.size.height - 2) * 0.8)

        if type(self.focused) == ListView:
            for _ in range(unit):
                self.focused.action_cursor_up()
        else:
            for _ in range(unit):
                self.control_target.scroll_up()

    def action_scroll_page_down(self):
        unit = int((self.app.size.height - 2) * 0.8)

        if type(self.focused) == ListView:
            for _ in range(unit):
                self.focused.action_cursor_down()
        else:
            for _ in range(unit):
                self.control_target.scroll_down()

    def action_focus_next(self):
        if self.state_show_input: return
        self.app.action_focus_next()

    def action_focus_previous(self):
        if self.state_show_input: return
        self.app.action_focus_previous()
        
    def action_grab_focus(self, reverse=False):
        if self.focused == None: return

        viewable_area = (self.control_target.scroll_offset.y, self.control_target.scroll_offset.y + self.control_target.size.height - 1)
        widget_area = (self.focused.virtual_region.y, self.focused.virtual_region.y + self.focused.virtual_region.height - 1)

        if (widget_area[1] < viewable_area[0] or viewable_area[1] < widget_area[0]) :

            if not reverse:
                xSet = (0, self.control_target.size.width)
                ySet = (1, self.control_target.size.height)
            else:
                xSet = (self.control_target.size.width - 1, -1, -1)
                ySet = (self.control_target.size.height - 1, 0, -1)

            for x in range(*xSet):
                for y in range(*ySet):
                    focused = self.app.get_widget_at(x, y)[0]

                    if focused is self.control_target or type(focused) == ScrollBar: continue
                    
                    if focused.can_focus: 
                        self.app.set_focus(focused)
                        return

    def action_release_focus(self):
        self.saved_focus = self.app.focused
        self.app.set_focus(None)

# ------------------------------------------------------------------------------------------------

# functions---------------------------------------------------------------------------------------
    def switch_container(self, main=False, help=False):
        if main == help == False: main = help = True

        if self.state_show_help == False and help:
            self.prompt_label.text = self.help_prompt_str
            self.main_container.styles.display = 'none'
            self.help_container.styles.display = 'block'
            self.control_target = self.help_container
            self.action_release_focus()
            self.state_show_help = True

        elif self.state_show_help == True and main:
            self.prompt_label.text = self.main_prompt_str
            self.main_container.styles.display = 'block'
            self.help_container.styles.display = 'none'
            self.control_target = self.main_container
            self.app.set_focus(self.saved_focus)
            self.state_show_help = False

    def switch_input_box(self, open=False, close=False, clear=False):
        if open == close == False: open = close = True

        if clear: self.input_box.value = ''

        if self.state_show_input == False and open:
            self.input_box.styles.display = 'block'
            self.input_last_focused = self.app.focused
            self.app.set_focus(self.input_box)
            self.state_show_input = True

        elif self.state_show_input == True and close:
            self.input_box.styles.display = 'none'
            self.app.set_focus(self.input_last_focused)
            self.state_show_input = False

    def request_input(self, getter, getter_args=(), placeholder='Need some Inputs.'):
        self.input_box.placeholder = placeholder
        self.switch_input_box(open=True)

        self.input_getter = getter
        self.input_getter_args = getter_args

    def __run_input_getter(self):
        self.input_getter(self, *self.input_getter_args)
        self.input_getter = lambda x: x
        self.input_getter_args = ()

    def remount_input_box(self):
        new_input_box = Input(self.input_box.value, self.input_box.placeholder)

        self.input_box.remove()
        self.app.mount(new_input_box)

        self.input_box = new_input_box
        self.input_box.styles.display = 'block' if self.state_show_input else 'none'

    def push_main_container(self, container:Container):
        self.main_container.remove()
        self.app.mount(container)
        self.main_container = container

        if self.state_show_help: self.main_container.styles.display = 'none'
        else: self.control_target = container

    def push_help_container(self, container:Container):
        self.help_container.remove()
        self.app.mount(container)
        self.help_container = container
        if self.state_show_help: self.control_target = container
        else: self.help_container.styles.display = 'none'
# -------------------------------------------------------------------------------------------------            

class Scene:
    def __init__(self, main_prompt='Empty main prompt.', contents:list=[], callbacks:list=[], callbacks_args:list=[], help_prompt='Empty help prompt.', help_doc:str='Empty help doc', multi_select=False) -> None:
        self.main_prompt = main_prompt
        self.contents = contents
        self.help_prompt = help_prompt
        self.help_doc = help_doc
        self.callbacks = callbacks
        self.callbacks_args = callbacks_args
        self.multi_select = multi_select

    def add(self, content, callback, callback_arg):
        self.contents.append(content)
        self.callbacks.append(callback)
        self.callbacks_args.append(callback_arg)
    
    def get_by_index(self, idx):
        return (self.contents[idx], self.callbacks[idx], self.callbacks_args[idx])

class Selector(TUIScreen):

    BINDINGS = [
        Binding('space', 'select_item', 'select', key_display='SPACE'),
        Binding('enter', 'submit', '', show=False, priority=True),
    ]

    def __init__(self, main_contents=[Label('Empty main contents.')], multi_select=False,
     help_contents=[Label('Empty help contents.')], main_prompt_str='Empty main prompt.', help_prompt_str='Empty help prompt', show_prompt=True) -> None:
        listview = self.build_listview(main_contents, multi_select)
        super().__init__([listview], help_contents, main_prompt_str, help_prompt_str, show_prompt)

        self.select_callback = None
        self.select_callback_args = None

        self.scene_stack = []

    def build_listview(self, str_list, multi_select=False):
        self.item_list = str_list
        self.contents_listview = ListView(*[(CheckableListItem(item, show_checkbox=multi_select))for item in self.item_list])
        self.multi_select = multi_select
        self.selected_items = {} if multi_select else None
        return self.contents_listview

    def action_select_item(self):
        self.contents_listview.action_select_cursor()

    def action_submit(self):
        if super().action_enter() == True: return

        if self.multi_select and len(self.selected_items) > 0:
            self.__run_select_callback()

    #TODO multi_select True에서 몇개 선택했는지 표시해주는 인디케이터 만들기
    def on_list_view_selected(self, event: ListView.Selected):
        if self.multi_select:
            if event.item.checked == False: 
                event.item.check_box = CheckableListItem.SYMBOL_CHECK
                event.item.checked = True
                self.selected_items[self.contents_listview.index] = self.item_list[self.contents_listview.index]
            else: 
                event.item.check_box = CheckableListItem.SYMBOL_UNCHECK
                event.item.checked = False
                self.selected_items.pop(self.contents_listview.index)
        else:
            self.selected_items = (self.contents_listview.index, self.item_list[self.contents_listview.index])
            self.__run_select_callback(self.contents_listview.index)

    def __run_select_callback(self, selected_idx):
        scene = self.scene_stack[-1]
        scene.callbacks[selected_idx](self, *(scene.callbacks_args[selected_idx]))

    def _change_scene(self, scene:Scene):
        self.main_prompt_str = scene.main_prompt
        self.push_main_container(Container(self.build_listview(scene.contents, scene.multi_select)))

        self.help_prompt_str = scene.help_prompt
        self.push_help_container(Container(Label(scene.help_doc, shrink=True)))

        self.prompt_label.text = self.help_prompt_str if self.state_show_help else self.main_prompt_str

    def push_scene(self, scene:Scene):
        try:
            if self.scene_stack[-1] is scene: return
        except IndexError: pass

        self._change_scene(scene)
        self.scene_stack.append(scene)

    def pop_scene(self):
        if len(self.scene_stack) > 1:
            self.scene_stack.pop()
            self._change_scene(self.scene_stack[-1])



#----------------------------------------------------------------------------------------------------------

# DUMMY_TEXT = '''\
# Velit. Lorem facilisi phasellus quam erat. Condimentum class fames orci cubilia mi felis urna. Primis posuere, etiam quisque Penatibus mauris luctus. Orci. Urna aptent nonummy vestibulum, sociosqu ad euismod Aliquam magna.
# Consequat mauris dictum tortor facilisi, conubia iaculis elementum mollis risus mus hendrerit. Inceptos ad fringilla. Mollis rhoncus diam condimentum donec, vulputate duis. Penatibus habitasse. Sit sodales, vestibulum, diam eros praesent, nisl quisque pharetra. Mattis sagittis Porta nec.
# Fames taciti pede hymenaeos sagittis. Molestie viverra. Ipsum penatibus lobortis cum sed vel mollis ut metus Ultrices arcu venenatis purus tellus fringilla libero fermentum ac ultricies hendrerit nam adipiscing interdum hendrerit, maecenas.
# Velit. Lorem facilisi phasellus quam erat. Condimentum class fames orci cubilia mi felis urna. Primis posuere, etiam quisque Penatibus mauris luctus. Orci. Urna aptent nonummy vestibulum, sociosqu ad euismod Aliquam magna.
# Consequat mauris dictum tortor facilisi, conubia iaculis elementum mollis risus mus hendrerit. Inceptos ad fringilla. Mollis rhoncus diam condimentum donec, vulputate duis. Penatibus habitasse. Sit sodales, vestibulum, diam eros praesent, nisl quisque pharetra. Mattis sagittis Porta nec.
# Fames taciti pede hymenaeos sagittis. Molestie viverra. Ipsum penatibus lobortis cum sed vel mollis ut metus Ultrices arcu venenatis purus tellus fringilla libero fermentum ac ultricies hendrerit nam adipiscing interdum hendrerit, maecenas.
# Velit. Lorem facilisi phasellus quam erat. Condimentum class fames orci cubilia mi felis urna. Primis posuere, etiam quisque Penatibus mauris luctus. Orci. Urna aptent nonummy vestibulum, sociosqu ad euismod Aliquam magna.
# Consequat mauris dictum tortor facilisi, conubia iaculis elementum mollis risus mus hendrerit. Inceptos ad fringilla. Mollis rhoncus diam condimentum donec, vulputate duis. Penatibus habitasse. Sit sodales, vestibulum, diam eros praesent, nisl quisque pharetra. Mattis sagittis Porta nec.
# Fames taciti pede hymenaeos sagittis. Molestie viverra. Ipsum penatibus lobortis cum sed vel mollis ut metus Ultrices arcu venenatis purus tellus fringilla libero fermentum ac ultricies hendrerit nam adipiscing interdum hendrerit, maecenas.
# Consequat mauris dictum tortor facilisi, conubia iaculis elementum mollis risus mus hendrerit. Inceptos ad fringilla. Mollis rhoncus diam condimentum donec, vulputate duis. Penatibus habitasse. Sit sodales, vestibulum, diam eros praesent, nisl quisque pharetra. Mattis sagittis Porta nec.
# Fames taciti pede hymenaeos sagittis. Molestie viverra. Ipsum penatibus lobortis cum sed vel mollis ut metus Ultrices arcu venenatis purus tellus fringilla libero fermentum ac ultricies hendrerit nam adipiscing interdum hendrerit, maecenas.
# Velit. Lorem facilisi phasellus quam erat. Condimentum class fames orci cubilia mi felis urna. Primis posuere, etiam quisque Penatibus mauris luctus. Orci. Urna aptent nonummy vestibulum, sociosqu ad euismod Aliquam magna.
# Consequat mauris dictum tortor facilisi, conubia iaculis elementum mollis risus mus hendrerit. Inceptos ad fringilla. Mollis rhoncus diam condimentum donec, vulputate duis. Penatibus habitasse. Sit sodales, vestibulum, diam eros praesent, nisl quisque pharetra. Mattis sagittis Porta nec.
# Fames taciti pede hymenaeos sagittis. Molestie viverra. Ipsum penatibus lobortis cum sed vel mollis ut metus Ultrices arcu venenatis purus tellus fringilla libero fermentum ac ultricies hendrerit nam adipiscing interdum hendrerit, maecenas.\
# '''

# ct1 = Container(
#     ListView(
#         *[(ListItem(Label(shrink=True ,renderable=f'hiasd;ajfasdji;flaj;sidflasjdfil;asdfjil;sdfjijalfsdasildjf isdajfasjdfilasdfjilasj ilasdjfi jasdilfaf jlasdjfajfilsd ajfaji falsdjfliadsjfliasdjflasdji asdj fsad{i}')))for i in range(100)]
#     ),
# )

# ct2 = Container(
#     Label(DUMMY_TEXT, shrink=True)
# )

# class my_btn(Button):
#     def __init__(self, label):
#         super().__init__(label)
#         self.styles.min_height = 3

# ct3 = Container(
#     *[Button(f'btn{i}')for i in range(20)]
# )

# ct4 = Container(
#     *[(Horizontal(Button(f'btn{i}'), Button(f'btn{i+1}')))for i in range(30)]
# )
# ct4.styles.overflow_y = 'scroll'


# DUMMY_LIST = [f'hi{i}' for i in range(100)]

# class MyApp(App):

#     BINDINGS = [
#         Binding('ctrl+a', 'push_main', 'push main'),
#         Binding('ctrl+b', 'push_help', 'push help'),
#     ]

#     def __init__(self):
#         super().__init__()

#     def on_mount(self):
#         self.install_screen(TUIScreen(), name='main')
#         self.install_screen(Selector(main_contents=DUMMY_LIST, multi_select=False), name='selector')
#         self.push_screen('selector')

#     def action_push_main(self):
#         selector:Selector = self.screen
#         selector.push_scene(scene1)
#         # self.screen.push_main_container(ct1)

#     def action_push_help(self):
#         # self.screen.request_input(Selector.change_title)
#         self.screen.push_help_container(ct2)

#     def change_title(screen:TUIScreen):
#         screen.prompt_label.text = screen.input_buffer

# def abc1(screen, a):
#     # LOG.writable(f'abc1 *args: {args}')
#     screen.prompt_label.text = f'abc1/{a}'

# def abc2(screen, a, b):
#     screen.prompt_label.text = f'abc2/{a}/{b}'

# def abc3(screen, a, b, c):
#     screen.prompt_label.text = f'abc3/{a}/{b}/{c}'        

# scene1 = Scene(
#     contents=[  
#         'hi1', 'hi2', 'hi3'
#     ],
#     help_doc='a simple scene change test, scene1',
#     callbacks=[
#         abc1, abc2, abc3
#     ],
#     callbacks_args=[
#         ('abc1_a',), ('abc2_a', 'abc2_b'), ('abc3_a', 'abc3_b', 'abc3_c')
#     ]
# )

# from datetime import datetime

# if __name__ == '__main__':
#     try:
#         # LOG = open('./log.txt', 'w')
#         # LOG.write(f'{datetime.now()}\n')
#         app = MyApp()
#         app.run()
#     except Exception as e:
#         print('Exception:', e)
#         # LOG.close()
