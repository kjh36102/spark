from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from TUI import TUIApp, InputContainer

from textual.message import Message, MessageTarget
from TUI_DAO import InputRequest
import asyncio

class InputSubmit(Message):

    def __init__(self, sender: MessageTarget, value) -> None:
        super().__init__(sender)
        self.value = value
        
class InputAborted(Message):
    
    def __init__(self, sender: MessageTarget) -> None:
        super().__init__(sender)

class ListSelected(Message):
    
    def __init__(self, sender: MessageTarget, index, item) -> None:
        super().__init__(sender)
        self.index = index
        self.item = item
        
class PopScene(Message):
    
    def __init__(self, sender: MessageTarget) -> None:
        super().__init__(sender)

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
    def __init__(self, app: 'TUIApp', *args) -> None:
        self.app = app
        self.args = args
        self.__current_coroutine = None
        self.__response = None
    
    async def main(self):
        self.stop()
        
    def run(self):
        if self.__current_coroutine == None:
            self.__current_coroutine = self.main()
            asyncio.ensure_future(self.__current_coroutine)
            
    def stop(self):
        async def _stop():
            self.__current_coroutine.close()
            self.__current_coroutine = None
            self.app.main_screen.input_container.hide()
            self.app.main_screen.input_container.clear()
                
        if self.__current_coroutine != None: asyncio.ensure_future(_stop())
            
    def is_running(self):
        return True if self.__current_coroutine != None else False
            
    def response_input(self, response):
        if self.__current_coroutine != None: self.__response = response
    
    async def request_input(self, request:'InputRequest', polling_interval=0.05):
        input_container:'InputContainer' = self.app.main_screen.input_container
        
        input_container.set(request.prompt, request.help_doc, request.hint)
        input_container.show()
        self.app.set_focus(input_container.input_box)

        while True:
            while self.__response == None: await asyncio.sleep(polling_interval)
            if request.essential: 
                if self.__response == '': self.__response = None; continue
                else: break
            else:
                if self.__response == '': self.__response = request.default
                break

        ret = self.__response
        self.__response = None
        
        return ret