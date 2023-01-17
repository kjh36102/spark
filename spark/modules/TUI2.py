from textual.app import App, events
from textual.driver import Driver
from textual.widgets import Label, Footer, Input, TextLog, ListView, ListItem
from textual.binding import Binding
from textual.containers import Container
from textual.reactive import reactive
from typing import Type
from pyautogui import press
from threading import Thread

class ReactiveLabel(Label):

    value = reactive('')

    def __init__(self, value,
     renderable = "", *, expand: bool = False, shrink: bool = False, markup: bool = True, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(renderable, expand=expand, shrink=shrink, markup=markup, name=name, id=id, classes=classes)
        self.value = value

    def render(self):
        return self.value

class CheckableListItem(ListItem):
    SYMBOL_UNCHECK = '[ ]'
    SYMBOL_CHECK = '[+]'
    check_box = reactive('[ ]')
    value = Label('')

    def __init__(self, value, check_box=False, checked=False,
    *children, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(*children, name=name, id=id, classes=classes)

        self.value = value
        self.checkbox = check_box
        self.checked = checked

        if checked: self.check_box = self.SYMBOL_CHECK
        
    def render(self):
        if self.checkbox: return f'{self.check_box}  {self.value}'
        else: return f'>  {self.value}'
    
    def toggle_check(self, app, item):
        if self.checked: self.uncheck()
        else: self.check()
    
    def check(self):
        self.check_box = self.SYMBOL_CHECK
        self.checked = True
    
    def uncheck(self):
        self.check_box = self.SYMBOL_UNCHECK
        self.checked = False

class InputRequest:
    def __init__(self, input_prompt, input_help='', hint='', default=None, password=False, essential=False, prevalue=''):
        self.input_prompt = input_prompt
        self.input_help = input_help
        self.hint = hint
        self.default = default
        self.password = password
        self.prevalue = prevalue
        self.essential = essential
        
class Scene:
    def __init__(self, items, main_prompt='Select what you want', logger_prompt='Logs', help_prompt='Show Help Doc', help_title='', help_content='', cursor=0, multi_select=False) -> None:
        self.main_prompt = main_prompt
        self.help_prompt = help_prompt
        self.logger_prompt = logger_prompt
        self.help_title = help_title
        self.help_content = help_content
        self.multi_select = multi_select
        self.cursor = cursor
        self.items = [CheckableListItem(item, check_box=multi_select) for item in items]
        self.list_view = ListView(*self.items)
        self.selected_items = {}


class TerminalApp(App):
    CSS='''\
#outer_prompt{
    background: rgb(0, 122, 204);
    width: 100%;
    height: 1;
    padding: 0 2 0 2;
    text-style: bold italic;
}

#input_container {
    background: red;
    min-height: 5;
    max-height: 6;
    text-style: bold;
    display: none;
}

#main_container {
    background: green;
}

#input_prompt {
    height: 1;
    background: purple;
    padding: 0 1 0 1;
}

#input_help {
    max-height: 2;
    background: orange;
    padding: 0 2 0 2;
}

#help_title {
    padding: 1 1 1 1;
    background: blue;
    text-style: bold;
}

#help_content {
    padding: 0 2 0 2;
    background: yellow;
}

#list_container {
    height: 100h;
}

#help_container {
    height: 100h;
    display: none;
}

#logger_container {
    height: 100h;
    display: none;
}

ListItem {
    padding: 0 1 0 1;
}
'''

    def __init__(self, 
        driver_class: Type[Driver] | None = None, css_path = None, watch_css: bool = False):
        super().__init__(driver_class, css_path, watch_css)

        #input container elements
        self.input_prompt = ReactiveLabel('input prompt', shrink=True, id='input_prompt')
        self.input_help = ReactiveLabel('input help', shrink=True, id='input_help')
        self.input_box = Input()

        #help elements
        self.help_title = ReactiveLabel('help title', shrink=True, id='help_title')
        self.help_content = ReactiveLabel('help content', shrink=True, id='help_content')

        #logger elements
        self.logger = TextLog(max_lines=100)
        self.loading_box = ReactiveLabel('[■■■■■■■■■■■■■■■■■] some loading box message', id='loading_box')

        #main elements
        self.list = ListView(*[CheckableListItem(f'hi{i}') for i in range(30)])
        self.list_container = Container(
            self.list,
            id='list_container'
        )
        self.help_container = Container(
            self.help_title, self.help_content,
            id='help_container'
        )
        self.logger_container = Container(
            self.logger, self.loading_box,
            id='logger_container'
        )

        #outer elements
        self.outer_prompt = ReactiveLabel('outer prompt', shrink=True, id='outer_prompt')
        self.input_container = Container(
            self.input_prompt,
            self.input_help,
            self.input_box,
            id='input_container'
        )
        self.main_container = Container(
            self.list_container, self.help_container, self.logger_container,
            id='main_container'
        )

        #display states
        self.show_input = False
        self.screen_state = 0   #0: list, 1: help, -1: logger

        self.main_prompt = ''
        self.help_prompt = ''
        self.logger_prompt = ''

        self.input_requests = []
        self.input_responses = [] #0: request, 1: value
        self.selected_items = None #tuple (scene, (idx, val)) | (scene, {idxs, vals})
        self.scenes = []

    def on_ready(self):
        #set initialize styles
        self.resize()
        self.set_focus(self.list)
        press('ctrl')    #for after use this faster

        #test base scene
        scene = Scene(items=[f'base{i}' for i in range(20)])
        self.push_scene(scene)

    def compose(self):
        yield self.outer_prompt
        yield self.input_container
        yield self.main_container
        yield Footer()

    async def _on_resize(self, event: events.Resize) -> None:
        self.resize()
        return await super()._on_resize(event)


    def _on_idle(self) -> None:
        if self.screen_state == 1:
            self.logger.write('Enter on resize')
        self.resize()   
        return super()._on_idle()

    #when input submitted
    def on_input_submitted(self, message: Input.Submitted):
        #if exist get first input_request
        if self.input_requests.__len__() > 0:
            request = self.input_requests[0]

            #check essential
            if message.value == '':
                if request.essential: return
                else: self.input_responses.append((request, request.default))
            else:
                self.input_responses.append((request, message.value))

            #push next request
            self.push_next_input_request()

    #on select list item
    def on_list_view_selected(self, message: ListView.Selected):
        self.selected_items[self.scenes[-1]] = (self.list.index, message.item.value)

    def resize(self):
        self.main_container.styles.height = self.app.size.height - (self.input_container.size.height + 2)

    BINDINGS = [
        Binding('h', 'show_help', 'help'),
        Binding('l', 'show_logger', 'log'),
        Binding('m', 'show_list', 'main'),
        Binding('i', 'toggle_input', 'input'),
        Binding('escape', 'press_esc', 'back'),
        Binding('ctrl+a', 'test1', 'test1'),
        Binding('ctrl+x', 'test2', 'test2'),
    ]

    def action_test1(self):

        scene = Scene(
            items=[f'zz{i}' for i in range(20)],
            main_prompt='Welcome test program!',
            help_prompt='Looking for help?',
            logger_prompt='gimotti log',
            help_title='How to use this app',
            help_content='blah blah slah slah',
            multi_select=False
        )

        self.push_scene(scene)
        pass

    def action_test2(self):

        self.request_input(
            InputRequest(
                input_prompt='what do you want to log',
                input_help='type anything you want',
                hint='anything',
                default='default',
                # essential=True,
                prevalue='zz'
            )
        )
        pass


    def action_show_help(self):
        self.screen_state = 1
        self.__set_screen_visiblity((0, 0, 1))
        self.__set_outer_prompt(self.scenes[-1])
        self.logger.write('push show help')

    def action_show_logger(self):
        self.screen_state = -1
        self.__set_screen_visiblity((1, 0, 0))
        self.__set_outer_prompt(self.scenes[-1])

    def action_show_list(self):
        self.screen_state = 0
        self.__set_screen_visiblity((0, 1, 0))
        self.__set_outer_prompt(self.scenes[-1])
        self.set_focus(self.list)
    
    def action_toggle_input(self):
        if self.show_input : self.close_input()
        else: self.open_input()
        press('tab')    #for remove scrollbar

    def action_press_esc(self):
        if self.show_input: self.close_input()
        elif self.screen_state != 0: self.action_show_list()
        else: self.pop_scene()

    def open_input(self):
        self.show_input = True
        self.input_container.styles.display = 'block'
        self.input_box.can_focus=True

    def close_input(self):
        self.show_input = False
        self.input_container.styles.display = 'none'
        self.input_box.can_focus=False
        self.set_focus(self.list)

    def __set_screen_visiblity(self, bits_3w):
        #adjust visiblity
        self.logger_container.styles.display = 'block' if bits_3w[0] == 1 else 'none'
        self.list_container.styles.display = 'block' if bits_3w[1] == 1 else 'none'
        self.help_container.styles.display = 'block' if bits_3w[2] == 1 else 'none'

    def __set_outer_prompt(self, scene):
        if self.screen_state == 0:
            self.main_prompt = scene.main_prompt
            self.outer_prompt.value = self.main_prompt
        elif self.screen_state == 1:
            self.help_prompt = scene.help_prompt
            self.outer_prompt.value = self.help_prompt
        elif self.screen_state == -1:
            self.logger_prompt = scene.logger_prompt
            self.outer_prompt.value = self.logger_prompt

    def __set_help(self, scene):
        #remove origin helps
        self.help_title.remove()
        self.help_content.remove()

        self.help_title = ReactiveLabel(scene.help_title, shrink=True, id='help_title')
        self.help_content = ReactiveLabel(scene.help_content, shrink=True, id='help_content')

        #mount
        self.help_container.mount(self.help_title, self.help_content)

    def push_scene(self, scene:Scene):
        #changing prompts and apply
        self.__set_outer_prompt(scene)

        #set current list hidden
        self.list.styles.display = 'none'

        #mount new list
        self.list_container.mount(scene.list_view)
        self.list = scene.list_view
        self.scenes.append(scene)

        #set focus on new list
        self.set_focus(self.list)

        self.__set_help(scene)

    def pop_scene(self):
        if self.scenes.__len__() > 1:
            #get previous scene
            prev_scene = self.scenes[-2]

            #set prompts
            self.__set_outer_prompt(prev_scene)

            #remove current list
            self.list.remove()

            #restore visibilit of prev list
            self.list = prev_scene.list_view
            self.list.styles.display = 'block'

            #set focus to prev list
            self.set_focus(self.list)

            self.__set_help(prev_scene)

            #pop last scene from stack
            self.scenes.pop()

    def __set_input(self, request:InputRequest):
        self.input_prompt.value = request.input_prompt
        self.input_help.value = request.input_help
        self.input_box.placeholder = request.hint
        self.input_box.value = request.prevalue
        self.input_box.password = request.password

    def clear_input(self):
        self.input_requests.clear()
        self.input_responses.clear()

        self.__set_input(InputRequest(input_prompt='There is no input request'))

    def request_input(self, request:InputRequest):
        self.input_requests.append(request)

        if self.input_requests.__len__() <= 1:
            self.push_next_input_request(request)

    def push_next_input_request(self):
        if self.input_requests.__len__() <= 0: return

        request:InputRequest = self.input_requests.pop(0)

        self.__set_input(request)

import time

class CustomProcess(Thread):
    def __init__(self, app:TerminalApp) -> None:
        super().__init__(daemon=True)
        self.app = app

    def get_input(self, count=1, polling_rate=0.1):

        ret_buf = []
        for _ in range(count):
            while self.app.input_responses.__len__() == 0: time.sleep(polling_rate)
            ret_buf.append(self.app.input_responses.pop(0))
        
        return ret_buf

    def get_select(self, scene:Scene, polling_rate=0.05):
        while self.app.selected_items == None: time.sleep(polling_rate)

        response_scene, selected = self.app.selected_items

        if scene != response_scene: return None

        return selected


class TestProcess(CustomProcess):
    def __init__(self, app: TerminalApp) -> None:
        super().__init__(app)

        self.funcs=[
            self.func1,
            self.func2,
            self.func3,
            self.func4,
        ]

        self.main_scene = Scene(
                items=[func.__name__ for func in self.funcs],
                main_prompt='Test Process',
                help_prompt='Test Process Help',
                logger_prompt='Test Process Log',
                help_title='Test Process Help Title',
                help_content='Test Process Help Content',
                # multi_select=True
            )

    def run(self):
        while True:
            #TODO 입력 요청해야함 push scene?, multiselect값 받는것도 해야함

    def func1(self):
        self.app.logger.write('called func1')

    def func2(self):
        self.app.logger.write('called func2')

    def func3(self):
        self.app.logger.write('called func3')

    def func4(self):
        self.app.logger.write('called func4')







if __name__ == '__main__':
    app = TerminalApp()
    app.run()


