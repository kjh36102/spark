from textual.message import Message, MessageTarget


class InputSubmit(Message):

    def __init__(self, sender: MessageTarget, input_request,) -> None:
        super().__init__(sender)
        
class InputAborted(Message):
    pass