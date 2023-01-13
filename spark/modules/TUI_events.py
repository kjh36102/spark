from textual.message import Message, MessageTarget


class InputSubmit(Message):

    def __init__(self, sender: MessageTarget, input_request,) -> None:
        super().__init__(sender)
        
class InputAborted(Message):
    pass


from threading import Thread
from TUI_DAO import InputRequest
from TUI2 import TUIApp, InputContainer
from time import sleep

class CustomProcess(Thread):
    def __init__(self, app:TUIApp) -> None:
        self.app = app
        self.running_state = False
        self.response = None
        
    def response_input(self, response):
        self.running_state = True
        self.response = response
        
    def request_input(self, request:InputRequest, polling_interval=0.1):
        input_container:InputContainer = self.app.main_screen.input_container
        
        input_container.set(request.prompt, request.help_doc, request.hint)
        input_container.show()
        self.app.set_focus(input_container.input_box)
        
        while self.response == None: sleep(polling_interval)
        
        ret = self.response
        self.response = None
        
        return ret
    
    
    
        
    
    