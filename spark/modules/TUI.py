from textual.app import App, events
from textual.widgets import ListView, ListItem, Label, Footer, Input, Footer, Button
from textual.reactive import reactive
from textual.binding import Binding
from textual.screen import Screen
from textual.containers import Container
from textual.scrollbar import ScrollBar
from textual.containers import Grid

from time import sleep
from threading import Thread

from types import FunctionType

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

    def __init__(self, text, classes=None, id=None, shrink=True, indent=True) -> None:
        super().__init__(classes=classes, id=id, shrink=shrink)
        self.text = text

        #styles
        self.styles.background = '#0053aa'
        self.styles.width = '100%'
        self.styles.text_style = 'bold'
        self.indent = indent

    def render(self) -> str:
        return ('  ' if self.indent else '') + self.text

class TUIScreen(Screen):
    BINDINGS = [
        Binding('escape', 'escape', 'back', priority=True),
        Binding('ctrl+n', 'toggle_input_box', 'toggle input', priority=True),
        Binding('ctrl+x', 'clear_input_box', 'clear input', priority=True),
        Binding('h', 'toggle_help', 'toggle help', priority=False),
        Binding('g', 'grab_focus', 'grab focus'),
        Binding('G', 'grab_focus(True)', 'grab focus', show=False),
        Binding('r', 'release_focus', 'release focus'),
        Binding('enter', 'enter', '', show=False, priority=True),
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
        self.input_request_buffer = []
        self.input_buffer = []
        # self.last_input_prompt = None
        self.input_getter_buffer = []
        self.saved_focus = None

        self.input_prompt_str = "There's nothing to input."
        self.input_placeholder = ''

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

            if self.app.focused is not self.input_box: return False

            if len(self.input_request_buffer) >= 2 :#and self.input_box.value != '':
                self.input_buffer.append(self.input_box.value)
                self.input_request_buffer.pop(0)
                self.switch_input_box(close=True, clear=True)

                #한 세트 끝났을 시
                if self.input_request_buffer[0] == False:
                    self.input_request_buffer.pop(0)
                    getter, getter_args = self.input_getter_buffer.pop(0)
                    # self.switch_input_box(close=True, clear=True)
                    getter(self, *getter_args)

                #한 세트 처리 후에도 요청이 남아있으면
                if len(self.input_request_buffer) > 0:
                    #요청버퍼에 남아있는 프롬프트 가져와서 input 프롬프트 업데이트
                    prompts = self.input_request_buffer[0]
                    self.set_input_prompt(prompts[0], prompts[1])
                    
                    #입력창 열기
                    self.switch_input_box(open=True, clear=True)

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


    def alert_line(self, text, time=3):
        def __alert(self:TUIScreen, text, time):
            self.prompt_label.text = text
            sleep(time)
            self.refresh_prompt()

        th = Thread(target=__alert, args=(self, text, time))
        th.daemon = True
        th.start()

    def refresh_prompt(self):
        self.prompt_label.text = self.help_prompt_str if self.state_show_help else self.main_prompt_str
        

# ------------------------------------------------------------------------------------------------

# functions---------------------------------------------------------------------------------------
    def switch_container(self, main=False, help=False):
        if main == help == False: main = help = True

        if self.state_show_help == False and help:
            self.state_show_help = True
            self.main_container.styles.display = 'none'
            self.help_container.styles.display = 'block'
            self.control_target = self.help_container
            self.action_release_focus()

        elif self.state_show_help == True and main:
            self.state_show_help = False
            self.main_container.styles.display = 'block'
            self.help_container.styles.display = 'none'
            self.control_target = self.main_container
            self.app.set_focus(self.saved_focus)
        
        if not self.state_show_input: self.refresh_prompt()
        


    def switch_input_box(self, open=False, close=False, clear=False):
        if open == close == False: open = close = True

        if clear: self.input_box.value = ''

        if self.state_show_input == False and open:
            self.state_show_input = True
            self.input_box.styles.display = 'block'
            self.input_last_focused = self.app.focused
            self.app.set_focus(self.input_box)
            self.prompt_label.text = self.input_prompt_str
            self.input_box.placeholder = self.input_placeholder 

        elif self.state_show_input == True and close:
            self.state_show_input = False
            self.input_box.styles.display = 'none'
            self.app.set_focus(self.input_last_focused)
            self.refresh_prompt()

    def set_input_prompt(self, prompt, placeholder):
        self.input_prompt_str = prompt
        self.input_placeholder = placeholder


    def request_input(self, prompt:tuple[str]|list[tuple], callback:FunctionType, callback_args:tuple=()):
        '''Make user to input something.

        Open input box and make user to input something.
        Callback function will called when user complete a set of request.
        This will not wait until user make some input.

        Args:
        
            prompt: prompt and hint
            callback:  which called when user complete requests
            callback_args (optional): callback arguments

        Example::

            def do_something(selector:Selector):

                prompts = [('Type ID', 'ID'), ('Type PW', 'PW'), ('Type Email', 'Email')]

                def my_callback(selector:Selector, arg1, arg2):
                    inputs = selector.get_input(len(prompts))
                    selector.alert_line(f'ID:{inputs[0]}, PW:{inputs[1]}, Email:{inputs[2]}')

                selector.request_input(prompts, my_callback, args=('arg1', 'arg2'))
        '''

        # 입력 요청을 버퍼에 추가
        if type(prompt) == list:
            for item in prompt:
                self.input_request_buffer.append(item)
        else: self.input_request_buffer.append(prompt)

        # 입력 요청 종료 구분자 추가
        self.input_request_buffer.append(False)

        # 입력 콜백 버퍼에 콜백함수 추가
        self.input_getter_buffer.append((callback, callback_args))

        # 요청 0번째 가져다 프롬프트 업데이트
        self.set_input_prompt(self.input_request_buffer[0][0], self.input_request_buffer[0][1])

        # 입력 창 띄우기
        self.switch_input_box(open=True, clear=True)

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
    
    def get_input(self, cnt:int=1):
        '''Get inputs from input buffer.

        After call ``Selector#request_input()``, get inputs from input buffer.
        This should be used in the callback function which passed in ``Selector#request_input()``

        Args:
        
            cnt: a number of how many inputs to get from buffer
            
        Returns:
            ``None`` if there's nothing in buffer else ``input | list[input]``

        Example::

            def do_something(selector:Selector):

                prompts = [('Type ID', 'ID'), ('Type PW', 'PW'), ('Type Email', 'Email')]

                def my_callback(selector:Selector, arg1, arg2):
                    inputs = selector.get_input(len(prompts))
                    selector.alert_line(f'ID:{inputs[0]}, PW:{inputs[1]}, Email:{inputs[2]}')

                selector.request_input(prompts, my_callback, args=('arg1', 'arg2'))
        '''
        if len(self.input_buffer) >= cnt:
            return self.input_buffer.pop(0) if cnt == 1 else [self.input_buffer.pop(0) for _ in range(cnt)]
        else: return None
# -------------------------------------------------------------------------------------------------            

class Scene:
    def __init__(self, main_prompt='Select what you want.', contents:list=[], callbacks:list=[], callbacks_args:list=[], help_prompt='Do you need help?', help_doc:str='Empty help doc', multi_select=False) -> None:
        self.main_prompt = main_prompt
        self.contents = contents
        self.help_prompt = help_prompt
        self.help_doc = help_doc
        self.callbacks = callbacks if len(callbacks) > 0 else [lambda x: x for _ in range(len(contents))]
        self.callbacks_args = callbacks_args if len(callbacks_args) > 0 else [() for _ in range(len(contents))]
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
        Binding('escape', 'escape', 'back', show=True, priority=True),
    ]

    def __init__(self, main_contents=[Label('Empty main contents.')], multi_select=False,
     help_contents=[Label('Empty help contents.')], main_prompt_str='Empty main prompt.', help_prompt_str='Empty help prompt', show_prompt=True) -> None:
        listview = self.build_listview(main_contents, multi_select)
        super().__init__([listview], help_contents, main_prompt_str, help_prompt_str, show_prompt)

        self.select_callback = None
        self.select_callback_args = None
        self.select_callback_reuse = False

        self.scene_stack = []

    def build_listview(self, str_list, multi_select=False):
        self.item_list = str_list
        self.contents_listview = ListView(*[(CheckableListItem(item, show_checkbox=multi_select))for item in self.item_list])
        self.multi_select = multi_select
        self.selected_items = {} if multi_select else None
        return self.contents_listview

    def action_select_item(self):
        if self.state_show_help: return
        
        self.contents_listview.action_select_cursor()

    def action_submit(self):
        if super().action_enter() == True: return

        if self.state_show_help: return

        if self.multi_select and len(self.selected_items) > 0:
            self.__run_select_callback()

    def action_escape(self):
        if self.state_show_input:
            self.switch_input_box(close=True, clear=True)
            self.clear_input_context()
        elif self.state_show_help:
            self.switch_container(main=True)
        else: 
            self.pop_scene()



    #TODO multi_select True에서 몇개 선택했는지 표시해주는 인디케이터 만들기
    def on_list_view_selected(self, event: ListView.Selected):
        self.switch_input_box(close=True, clear=True)

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
            self.__run_select_callback()

    def set_select_callback(self, callback, callback_args=(), reuse=False):
        self.select_callback = callback
        self.select_callback_args = callback_args
        self.select_callback_reuse = reuse

    def get_selected_items(self):
        ret = self.selected_items
        self.selected_items = {} if self.multi_select else None
        return ret

    def __run_select_callback(self):
        if self.select_callback == None:
            scene:Scene = self.scene_stack[-1]
            idx = self.contents_listview.index
            scene.callbacks[idx](self, *(scene.callbacks_args[idx]))
        else:
            self.select_callback(self, *self.select_callback_args)
            if not self.select_callback_reuse:
                self.select_callback = None
                self.select_callback_args = None

    def _change_scene(self, scene:Scene):
        self.clear_context()

        self.main_prompt_str = scene.main_prompt
        self.push_main_container(Container(self.build_listview(scene.contents, scene.multi_select)))

        self.help_prompt_str = scene.help_prompt
        self.push_help_container(Container(Label(scene.help_doc, shrink=True)))

        self.app.action_focus_next()

        self.refresh_prompt()

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
        
    def clear_input_context(self):
        if len(self.input_request_buffer) > 0:
            self.input_buffer.clear()
            self.input_request_buffer.clear()
            self.input_getter_buffer.clear()

        self.set_input_prompt("There's nothing to input.", '')

    def clear_context(self, callback_alive=False):
        self.clear_input_context()

        if callback_alive == False:
            self.select_callback = self.select_callback_args = None
            self.select_callback_reuse = False
            
    def remove_list_item(self, index):
        self.contents_listview.children[index].remove()
        self.contents_listview.refresh(repaint=True, layout=True)
        # self.set_focus(self.contents_listview)
        # self.contents_listview.action_cursor_down
        # remain_children = self.contents_listview.children._nodes
        # self.contents_listview.clear()
        # for item in remain_children:
        #     self.contents_listview.append(item)
        # self.contents_listview.children._nodes.pop(index)
        # self.contents_listview

def get_func_names(funcs):
    return [(func.__name__).replace('_', ' ') for func in funcs]


class AlertScreen(Screen):
    BINDINGS = [
        Binding('space', 'space', 'select', show=False, priority=True),
        Binding('enter', 'enter', 'leave', show=False, priority=True),
    ]

    def action_space(self):
        self.button.press()
    
    def action_enter(self):
        self.button.press()

    def __init__(self, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name, id, classes)

        self.prompt_label = ReactiveLabel('Alert')
        self.label = ReactiveLabel("Empty contents", id="question", indent=False)
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
        yield self.prompt_label
        yield self.grid
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.pop_screen()

    async def _on_resize(self, event: events.Resize) -> None:
        self.button.styles.margin = (0, 0, 0, int(((self.app.size.width) - self.button.size.width) / 2))
        return await super()._on_resize(event)