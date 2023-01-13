from TUI2 import TUIApp, CustomProcess, InputRequest, Binding
import time
import asyncio
class SparkTest(TUIApp):
    def __init__(self):
        super().__init__()

    BINDINGS = [
        Binding('ctrl+a', 'test1', 'test1'),
        Binding('ctrl+b', 'test2', 'test2'),
        Binding('ctrl+x', 'test3', 'test3'),
        Binding('ctrl+z', 'test4', 'test4')
    ]
    
    def action_test1(self):
        self.main_screen.run_custom_process(TestChangePromptProcess(self))
        pass
    
    def action_test2(self):
        async def count_up():
            self.main_screen.prompt.value = '0'
            for _ in range(10):
                self.main_screen.prompt.value = str(int(self.main_screen.prompt.value) + 1)
                self.main_screen.prompt.refresh()
                await asyncio.sleep(1)

        asyncio.ensure_future(count_up())

        # loop = asyncio.get_running_loop()
        

        # process = CustomProcess(self)
        # process.register(count_up)
        # process.start()
        pass
        
    def action_test3(self):
        pass
        
    def action_test4(self):
        pass

class TestChangePromptProcess(CustomProcess):
    def __init__(self, app) -> None:
        super().__init__(app)

    def run(self):
        new_prompt = self.request_input(InputRequest(
            prompt='프롬프트 변경',
            help_doc='입력한 값으로 프롬프트 텍스트를 변경합니다.',
            hint='텍스트'
        ))

        self.app.main_screen.prompt.value = new_prompt

        want_exit = self.request_input(InputRequest(
            prompt='프로그램 종료',
            help_doc='프로그램을 종료하시겠습니까?',
            hint='y/n'
        ))

        if want_exit == 'y': self.app.exit()


    
if __name__ == '__main__':
    app = SparkTest()
    app.run()