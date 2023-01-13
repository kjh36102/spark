from textual.message import Message, MessageTarget


class InputSubmit(Message):

    def __init__(self, sender: MessageTarget, value) -> None:
        super().__init__(sender)
        self.value = value
        
class InputAborted(Message):
    pass

    
    
    
        
    
    