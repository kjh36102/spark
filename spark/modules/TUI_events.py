from textual.message import Message, MessageTarget

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
    