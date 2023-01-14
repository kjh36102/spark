from TUI2 import TUIApp, InputRequest, Binding
from TUI_DAO import Scene
from TUI_Widgets import CheckableListItem

from CustomProcess import CustomProcess

class TestChangePromptProcess(CustomProcess):
    def __init__(self, app) -> None:
        super().__init__(app)

    async def main(self):
        new_prompt = await self.request_input(InputRequest(
            prompt='프롬프트 변경',
            help_doc='입력한 값으로 프롬프트 텍스트를 변경합니다.',
            hint='텍스트'
        ))

        self.app.main_screen.prompt.value = new_prompt

        want_exit = await self.request_input(InputRequest(
            prompt='프로그램 종료',
            help_doc='프로그램을 종료하시겠습니까?',
            hint='y/n'
        ))

        if want_exit == 'y': self.app.exit()
        else: self.app.alert('취소됨', '취소되었습', '니', '다')
        
        self.app.print('coroutine end')
        
        return await super().main()
    
class TestFormProcess(CustomProcess):
    def __init__(self, app: TUIApp) -> None: super().__init__(app)
    async def main(self):
               
        
        return await super().main()
    
class SparkTest(TUIApp):
    def __init__(self):
        super().__init__()

    BINDINGS = [
        Binding('ctrl+a', 'test1', 'test1'),
        Binding('ctrl+b', 'test2', 'test2'),
        # Binding('ctrl+x', 'test3', 'test3'),
        # Binding('ctrl+z', 'test4', 'test4')
    ]
    
    def action_test1(self):
        self.run_custom_process(TestChangePromptProcess(self))
        pass
    
    def action_test2(self):
        items = [CheckableListItem(f'yo{i}') for i in range(10)]
        
        scene = Scene(
            main_prompt='테스트 씬1',
            items=items,
            help_prompt='테스트 도움말1',
            help_title='테스트 도움말 제목1',
            help_doc='테스트 도움말 문서1'
        )
        
        self.main_screen.push_scene(scene)
        pass
        
    def action_test3(self):
        pass
        
    def action_test4(self):
        pass




    
if __name__ == '__main__':
    app = SparkTest()
    app.run()