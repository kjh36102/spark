from textual.message import Message, MessageTarget


class InputSubmit(Message):

    def __init__(self, sender: MessageTarget, value) -> None:
        super().__init__(sender)
        self.value = value
        
class InputAborted(Message):
    pass


from threading import Thread
from TUI_DAO import InputRequest
from TUI2 import TUIApp, InputContainer
from time import sleep
import ctypes


    
    
    
        
    
    