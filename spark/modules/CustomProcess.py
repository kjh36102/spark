from TUI_DAO import InputRequest
from TUI2 import TUIApp, InputContainer
import asyncio

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
    def __init__(self, app:TUIApp) -> None:
        self.app = app
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
    
    async def request_input(self, request:InputRequest, polling_interval=0.1):
        input_container:InputContainer = self.app.main_screen.input_container
        
        input_container.set(request.prompt, request.help_doc, request.hint)
        input_container.show()
        self.app.set_focus(input_container.input_box)

        while self.__response == None: await asyncio.sleep(polling_interval)

        ret = self.__response
        self.__response = None
        
        return ret