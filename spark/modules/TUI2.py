from textual.app import App, events
from textual.binding import Binding
from textual.screen import Screen
from textual.containers import Container
from textual.widgets import Label, Footer, ListView, ListItem, TextLog, Input
from textual.reactive import reactive
from rich.console import RenderableType
from textual.color import Color
from textual.message_pump import messages
from textual.scrollbar import ScrollDown

import TUI_events
from TUI_DAO import *

from enum import Enum, auto
import time
import asyncio

class ReactiveLabel(Label):
    value = reactive('')
    
    def __init__(self, value, shrink=True) :
        super().__init__(shrink=shrink)
        self.set_text(value)
        
    def __call__(self, value):
        self.set_text(value)
        
    def set_text(self, value):
        self.value = value
    
    def render(self):
        return self.value

class Prompt(ReactiveLabel):
    def __init__(self, value) :
        super().__init__(value)
        
        #styles
        self.styles.background = '#0053aa'
        self.styles.width = '100%'
        self.styles.text_style = 'bold'
        
    def render(self):
        return '  ' + self.value
    
class CheckableListItem(ListItem):
    SYMBOL_UNCHECK = '[ ]'
    SYMBOL_CHECK = '[+]'
    check_box = reactive('[ ]')
    value = ReactiveLabel('')

    def __init__(self, value, checked=False, show_checkbox=True) -> None:
        super().__init__()

        self.value = value
        self.checked = checked
        self.show_checkbox = show_checkbox

        if checked: self.check_box = self.SYMBOL_CHECK
        
    def render(self):
        if self.show_checkbox: return f' {self.check_box}  {self.value}'
        else: return f' >  {self.value}'


DUMMY_LONG = '''\
Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.
Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section 1.10.32.
Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.
Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section 1.10.32.\
'''

DUMMY_SHROT = '''\
Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.\
'''

class InputContainer(Container):
    
    def __init__(self):

        self.prompt_origin = ''
        self.help_doc_origin = ''
        
        self.prompt = ReactiveLabel('')
        self.prompt_container = Container(self.prompt)
        
        self.help_doc = ReactiveLabel('')
        self.help_doc_container = Container(self.help_doc)
        
        self.input_box = Input()
            
        self.prompt.shrink = self.help_doc.shrink = self.input_box.shrink = True
        
        self.prompt_container.styles.overflow_y = self.help_doc_container.styles.overflow_y = 'hidden'
        
        self.prompt_container.styles.margin = (0, 1, 0, 1)
        self.help_doc_container.styles.margin = (0, 1, 0, 3)
        
        self.prompt.styles.text_style = 'bold'
        
        self.prompt.styles.width = self.help_doc.styles.width = '100%'
        
        self.state_display = False
        
        self.resize_flag = False
        
        super().__init__(
            self.prompt_container,
            self.help_doc_container,
            self.input_box
        )
        
    async def _on_compose(self) -> None:
        self.hide()
        return await super()._on_compose()
        
    def on_mount(self):
        self.prompt_container.styles.height = 1
        self.help_doc_container.styles.height = 0
        # self.styles.height = 5
        
        self.set(DUMMY_SHROT, DUMMY_LONG, 'This is input hint')
        
    async def _on_idle(self, event: events.Idle) -> None:
        if self.resize_flag: 
            self.resize_flag = False
            self.resize()
            self.help_doc_container.styles.display = 'none' if self.help_doc.value == '' else 'block'
        return await super()._on_idle(event)
    
    async def on_resize(self) -> None:
        self.resize()
        
    BINDINGS = [
        Binding('ctrl+x', 'expand_input_help', 'expand', priority=True),
        Binding('enter', 'submit_input', 'submit', priority=True),
    ]
    
    def action_expand_input_help(self):
        help_screen:HelpScreen = self.app.get_screen('help')
        
        help_screen.set(
            'Expanded input help doc',
            self.prompt_origin,
            self.help_doc_origin
            )
        
        self.app.push_screen(help_screen)
        
    async def action_submit_input(self):
        await self.emit(TUI_events.InputSubmit(sender=self))
        
    def __set(self, prompt, help_doc, hint):
        self.prompt.value = prompt
        self.help_doc.value = help_doc
        self.input_box.placeholder = hint
        
        self.resize_flag = True
    
    def set(self, prompt, help_doc='', hint=''):
        self.prompt_origin = prompt
        self.help_doc_origin = help_doc
            
        self.__set(self.prompt_origin, self.help_doc_origin, hint)

    def clear(self):
        self.prompt_origin = 'There is no input request.'
        self.help_doc_origin = ''
        
        self.__set(self.prompt_origin, self.help_doc_origin, '')
 
    def show(self):
        self.state_display = True
        self.styles.display = 'block'
        pass
    
    def hide(self):
        self.state_display = False
        self.styles.display = 'none'
        pass
    
    def resize(self):
        prompt_max_width = self.app.size.width - 2
        help_doc_max_width = (self.app.size.width - 4) * 2
        
        if len(self.prompt_origin) > prompt_max_width:
            self.prompt.value = self.prompt_origin[:prompt_max_width - 10] + ' .....'
            
        if len(self.help_doc_origin) > help_doc_max_width:
            self.help_doc.value = self.help_doc_origin[:help_doc_max_width - 15] + ' .....'
            
        self.help_doc_container.styles.height = min(2, self.help_doc.size.height)
        self.styles.height = self.prompt_container.size.height + self.help_doc_container.size.height + 3
        
        
class ListContainer(Container):
    def __init__(self, multi_select=False) -> None:
        self.list = ListView(ListItem(Label('Empty list')))
        super().__init__(self.list)
        self.multi_select = multi_select
        
        self.list.styles.min_height = 0
        self.styles.min_height = 0
        
    def push_list(self, items):
        self.list.clear()
        for item in items:
            self.list.append(CheckableListItem(value=item, show_checkbox=self.multi_select))

class LoadingBox(ReactiveLabel):
    def __init__(self, ratio=0, msg=''):
        super().__init__('')
        self.styles.width = '100%'
        self.ratio = ratio
        self.msg = msg
        
    def on_mount(self):
        self.set_bar(self.ratio, self.msg)
        
    def __call__(self, ratio, msg):
        self.set_bar(ratio, msg)        
        
    def set_bar(self, ratio, msg):
        if ratio < 0: ratio = 0
        elif ratio > 1: ratio = 1
        self.ratio = ratio
        self.msg = msg
        
        max_width = 20
        bar_len = int(max_width * ratio)
        bar = '■' * bar_len
        remain = ' ' * (max_width - bar_len)
        
        msg_width = self.app.size.width - (max_width + 4)
        if len(msg) > msg_width: fit_msg = msg[:msg_width - 3] + '...'
        else: fit_msg = msg
        
        self.value = '[' + bar + remain + '] ' + fit_msg
        
    def hide(self):
        self.styles.height = 0
        self.styles.display = 'none'
        
    def show(self):
        self.styles.height = 1
        self.styles.display = 'block'
        
    def clear(self):
        self.set_bar(0, '')


class HelpScreen(Screen):
    def __init__(self, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name, id, classes)
        
        self.prompt = Prompt('Empty prompt.')
        self.resize_flag = False
    
    def compose(self):
        yield self.prompt
        # yield self.contents_container
        yield Footer()
        
    def on_mount(self):
        self.set('Empty help prompt.', 'Empty help title.', 'Empty help doc.')
        
        
    async def _on_resize(self, event: events.Resize) -> None:
        self.resize()
        return await super()._on_resize(event)
        
        
    BINDINGS = [
        Binding('escape', 'pop_screen()', 'back'),
        Binding('up', 'scroll_up', 'up'),
        Binding('down', 'scroll_down', 'down'),
        Binding('pageup', 'scroll_page_up', 'pageup'),
        Binding('pagedown', 'scroll_page_down', 'pagedown'),
        Binding('home', 'scroll_home', 'home'),
        Binding('end', 'scroll_end', 'end'),
        # Binding('ctrl+a', 'test1', 'rm ct'),
        # Binding('ctrl+b', 'test2', 'mt ct'),
        # Binding('ctrl+x', 'test3', 'resize'),
    ]
    
    # def action_test1(self):
    #     self.contents_container.remove()
        
    # def action_test2(self):

    
    # def action_test3(self):
    #     self.resize()
    
    def set(self, prompt, help_title, help_doc):
        try: self.contents_container.remove()
        except AttributeError: pass
        
        self.prompt.value = prompt
        
        self.help_title = Label(help_title, shrink=True, classes='help_title')
        self.help_title_container = Container(self.help_title, classes='help_title_container')
        
        self.help_doc = Label(help_doc, shrink=True)
        self.help_doc_container = Container(self.help_doc, classes='help_doc_container')
        
        self.contents_container = Container()
        
        self.mount(self.contents_container)
        
        self.contents_container.mount(self.help_title_container)
        self.contents_container.mount(self.help_doc_container)
    
        #styles
        self.help_title_container.styles.height = self.help_doc_container.styles.height = 1
        self.help_title_container.styles.margin = (0, 1, 0, 1)
        self.help_doc_container.styles.margin = (0, 1, 0 ,3)
        self.help_title.styles.text_style = 'bold'
        
        self.resize_flag = True
    
    #이거 없으면 내용 바꿔도 업뎃안됨 ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ 내 12시간ㅋㅋ 응 지워봐~ 안하면 그만이야~
    async def _on_idle(self, event: events.Idle) -> None:
        if self.resize_flag: self.resize(); self.resize_flag = False
        return await super()._on_idle(event)
        

        
    
    def action_scroll_up(self):
        self.contents_container.action_scroll_up()
        
    def action_scroll_down(self):
        self.contents_container.action_scroll_down()
        
    def action_scroll_home(self):
        self.contents_container.action_scroll_home()
        
    def action_scroll_end(self):
        self.contents_container.action_scroll_end()
        
    def action_scroll_page_up(self):
        unit = int((self.app.size.height - 2) * 0.8)
        for _ in range(unit): self.contents_container.action_scroll_up()
        
    def action_scroll_page_down(self):
        unit = int((self.app.size.height - 2) * 0.8)
        for _ in range(unit): self.contents_container.action_scroll_down()
    
    def resize(self):
        app.print('resize called')
        
        self.help_title_container.styles.height = self.help_title.size.height
        self.help_doc_container.styles.height = self.help_doc.size.height
        self.contents_container.styles.height = self.app.size.height - 2

    def clear(self):
        self.prompt.value = ''
        self.help_title.value = ''
        self.help_doc.value = ''
        
class FormScreen(Screen):
    pass

class LoggerScreen(Screen):
    def __init__(self, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name, id, classes)
        
        self.prompt = Prompt('Empty prompt.')
        self.logger = TextLog(max_lines=200)
        self.loading_box = LoadingBox()
        
    def compose(self):
        yield self.prompt
        yield self.logger
        yield self.loading_box
        yield Footer()
        
    def on_mount(self):
        self.close_loading_box()
        
    BINDINGS = [
        Binding('ctrl+a', 'test1', 'test1'),
        Binding('escape', 'pop_screen()', 'back'),
        Binding('up', 'scroll_up', 'up'),
        Binding('down', 'scroll_down', 'down'),
        Binding('pageup', 'scroll_page_up', 'pageup'),
        Binding('pagedown', 'scroll_page_down', 'pagedown'),
        Binding('home', 'scroll_home', 'home'),
        Binding('end', 'scroll_end', 'end'),
    ]
    
    def action_scroll_up(self):
        self.logger.action_scroll_up()
        
    def action_scroll_down(self):
        self.logger.action_scroll_down()
        
    def action_scroll_home(self):
        self.logger.action_scroll_home()
        
    def action_scroll_end(self):
        self.logger.action_scroll_end()
        
    def action_scroll_page_up(self):
        unit = int((self.app.size.height - 2) * 0.8)
        for _ in range(unit): self.logger.action_scroll_up()
        
    def action_scroll_page_down(self):
        unit = int((self.app.size.height - 2) * 0.8)
        for _ in range(unit): self.logger.action_scroll_down()
    
    def action_test1(self):
        self.print('hello world')
        
    def open_loading_box(self):
        self.logger.styles.height = self.app.size.height - 3
        self.loading_box.show()
        
    def close_loading_box(self):
        self.logger.styles.height = self.app.size.height - 2
        self.loading_box.hide()
        
    def print(self, text):
        self.logger.write(text)




class MainScreen(Screen):
    
    def __init__(self, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name, id, classes)
        self.prompt = Prompt('Empty prompt')
        self.input_container = InputContainer()
        self.list_container = ListContainer()
        self.help_prompt = 'Empty help prompt.'
        self.help_title = 'Empty help title.'
        self.help_doc = 'Empty help doc.'
        
        self.input_requests = []
        
    def compose(self):
        yield self.prompt
        yield self.input_container
        yield self.list_container
        yield Footer()
    
    def on_mount(self):
        self.list_container.push_list([f'hi{i}' for i in range(50)])
    
    def on_submit_input(self, event: TUI_events.InputSubmit):
        pass
        
        
    BINDINGS = [
        Binding('h', 'open_help', 'open help'),
        Binding('l', 'push_screen("logger")', 'open logger'),
        Binding('i', 'toggle_input_container', 'toggle input'),
        Binding('escape', 'release_focus', 'back'),
    ]
    
    def action_open_help(self):
        help_screen:HelpScreen = self.app.get_screen('help')
        help_screen.set(self.help_prompt, self.help_title, self.help_doc)
        self.app.push_screen(help_screen)
        pass

    def action_toggle_input_container(self):
        if self.input_container.state_display == False: 
            self.input_container.show()
        else: 
            self.input_container.hide()
            
    def action_release_focus(self):
        self.app.set_focus(None)



class SubmitFlag(Enum):
    IDLE = auto()
    SUBMITTED = auto()
    VALID = auto()
    INVALID = auto()
    ABORTED = auto()


class TUIApp(App):
    
    def __init__(self, ):
        super().__init__()
        self.main_screen = MainScreen()
        self.logger_screen = LoggerScreen()
        self.help_screen = HelpScreen()
        
        self.submit_flag = SubmitFlag.IDLE
        
    def on_mount(self):
        #install main screen
        self.install_screen(self.main_screen, name='main')
        
        #install logger screen
        self.install_screen(self.logger_screen, name='logger')
        
        #install help screen
        self.install_screen(self.help_screen, name='help')
        
        #install form screen
        
        #push main screen
        self.push_screen('main')
        pass
        
    BINDINGS = [
        Binding('ctrl+a', 'test1', 'test1'),
        Binding('ctrl+b', 'test2', 'test2'),
        Binding('ctrl+x', 'test3', 'test3'),
        Binding('ctrl+z', 'test4', 'test4')
    ]
    
    # def on_input_submit(self, message: TUI_events.InputSubmit):
    #     self.submit_flag = SubmitFlag.SUBMITTED
    #     self.main_screen.input_container.clear()
    
    async def test1(self):
        # pass
        request = InputRequest(
            prompt='프롬프트 변경',
            help_doc='입력한 값으로 프롬프트 텍스트를 변경합니다.',
            hint='텍스트'
        )
        
        def checker(value):
            if type(value) != str: return '자료형이 올바르지 않습니다.'
            if value == 'no': return '그 단어는 사용할 수 없습니다.'
            return True
        
        code, value = self.request_input(
            request=request,
            valid_checker=checker
        )
        
        if code == SubmitFlag.VALID: self.main_screen.prompt.value = value
    
    async def action_test1(self):
        await asyncio.create_task(self.test1())
        pass
    
    def action_test2(self):
        pass
        
    def action_test3(self):
        pass
        
    def action_test4(self):
        pass
    
    def print(self, *texts):
        text =' '.join(texts)
        self.logger_screen.print(text)
    
    
    def request_input(self, request:InputRequest, valid_checker=(lambda x: True), valid_checker_args=(), polling_interval=0.1):
        main_screen:MainScreen = self.get_screen('main')
        input_container:InputContainer = main_screen.input_container
        
        input_container.set(request.prompt, request.help_doc, request.hint)
        main_screen.action_toggle_input_container()
        self.set_focus(input_container.input_box)

        ret = (self.submit_flag, None)
        while True:
            if self.submit_flag == SubmitFlag.SUBMITTED:
                submit_value = input_container.input_box.value
                msg = valid_checker(submit_value, *valid_checker_args)
                if msg == True: ret = (SubmitFlag.VALID, submit_value)
                else: ret = (SubmitFlag.INVALID, msg)
                break
            elif self.submit_flag == SubmitFlag.ABORTED:
                input_container.clear()
                ret = (SubmitFlag.ABORTED, None)
                break
            time.sleep(polling_interval)
            
        
        self.submit_flag = SubmitFlag.IDLE
        return ret
        

if __name__ == '__main__':
    app = TUIApp()
    app.run()    
