import sys
sys.path.append('./spark/modules/')
sys.path.append('./spark/modules/pages/')

from TUI import CustomProcess, TUIApp
from TUI_DAO import Scene, InputRequest, get_func_names

class MyCustomProcess(CustomProcess):
    def __init__(self, app: 'TUIApp') -> None:
        super().__init__(app)

        self.funcs = [

        ]

        func_names = get_func_names(self.funcs)

        self.scene = Scene(
            items=func_names,
            main_prompt='Your_Prompt',
        )

    async def main(self):
        idx, val = await self.request_select(self.scene)
        await self.funcs[idx]()