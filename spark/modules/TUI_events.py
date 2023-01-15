from __future__ import annotations

from typing import TYPE_CHECKING
from types import CoroutineType

if TYPE_CHECKING:
    from TUI import TUIApp, InputContainer

from TUI_DAO import InputRequest, Scene
import asyncio
from pyautogui import press

class CustomProcess:
    '''Create your own process runs inside TUIApp.
    
    You can inherit this class to create your own process that runs inside TUIApp.
    You should override native coroutine `async def main()`
    
    Example::

        class YourCustomProcess(self):
            def __init__(self, app):
                super().__init__(app)
            
            #overrided
            async def main(self):
                received_input_value = await self.request_input(InputRequest(
                    prompt='Change the prompt.',
                    help_doc='You can change the prompt value with your inputs.',
                    hint='any text'
                ))
                
                #do_something_with_received
                
                return await super().main() #this is necessary
                
    And inside of the TUIApp for run main()
    
    Example::

        BINDINGS = [
            Binding('ctrl+a', 'test', 'run action_test()'),
        ]

        def action_test(self):
            self.run_custom_process(YourCustomProcess(self))
            

    '''
    class AbortedException(Exception):
        pass
    
    class SubScenePopRequest(Exception):
        pass
    
    def __init__(self, app: 'TUIApp', *args) -> None:
        self.app = app
        self.args = args
        self.__current_coroutine = None
        self.__response_input = None
        self.__response_select = None
        self.__abort_flag = False
        self.__waiting_input_flag = False
        self.return_from_child = None
        # self.subscene_stack = []
        
    
    async def main(self):
        self.stop()
        
    def start(self, force=False):
        if self.__current_coroutine == None or force:
            self.__current_coroutine = self.main()
            asyncio.ensure_future(self.__current_coroutine)
    
    # def pop_subscene(self):
    #     self.app.push_scene(self.subscene_stack.pop())
    
    def stop(self):
        async def _stop():
            self.__current_coroutine.close()
            self.__current_coroutine = None
            
        if self.__current_coroutine != None: 
            asyncio.ensure_future(_stop())
            
    def is_running(self):
        return True if self.__current_coroutine != None else False
    
    def is_waiting_input(self):
        return self.__waiting_input_flag
            
    def response_input(self, response):
        if self.__current_coroutine != None: self.__response_input = response
    
    async def request_input(self, request:'InputRequest', polling_interval=0.05):
        '''
        run with await
        return user input
        '''
        input_container:'InputContainer' = self.app.main_screen.input_container
        
        input_container.set(request.prompt, request.help_doc, request.hint, password=request.password, previous=request.previous)
        input_container.show()
        # self.app.set_focus(input_container.input_box)
        
        press(['space', 'backspace']) #use pyautogui for refresh input box

        while True:
            self.__waiting_input_flag = True
            # self.app.print_log('waiting flag set true')
            while self.__response_input == None: 
                if self.__abort_flag:
                    self.__abort_flag = False
                    self.__waiting_input_flag = False
                    raise self.AbortedException
                await asyncio.sleep(polling_interval)
                
            if request.essential: 
                if self.__response_input == '': self.__response_input = None; continue
                else: break
            else:
                if self.__response_input == '': self.__response_input = request.default
                break

        ret = self.__response_input
        self.__response_input = None
        self.__waiting_input_flag = False
        
        return ret
    
    def response_select(self, response):
        if self.__current_coroutine != None: self.__response_select = response
        
    async def abort_input(self):
        if self.__current_coroutine != None:
            self.__abort_flag = True
    
    async def request_select(self, scene:Scene, polling_interval=0.05):
        '''
        run with await
        return idx, val
        '''
        
        self.app.push_scene(scene)
        
        while self.__response_select == None: await asyncio.sleep(polling_interval)
        
        ret = self.__response_select
        self.__response_select = None
        
        return ret
    
    async def request_from_child(self, subprocess:CustomProcess, polling_interval=0.05):
        
        self.app.run_custom_process(subprocess)
        
        while self.return_from_child == None: await asyncio.sleep(polling_interval)
        
        ret = self.return_from_child
        self.return_from_child = None
        
        return ret

    def return_to_parent(self, value):
        self.app.custom_process_stack[-2].return_from_child = value
        self.app.pop_custom_process()
    
    async def run(self, target, args=()):
        try:
            coro = target(self, self.app, *args)
        
            if type(coro) == CoroutineType:
                self.app.print_log('run coro')
                coro = await coro
            
            return coro
        except self.AbortedException: pass