from __future__ import annotations

from typing import TYPE_CHECKING
from types import CoroutineType

if TYPE_CHECKING:
    from TUI import TUIApp, InputContainer

from TUI_DAO import InputRequest, Scene, CheckableListItem
import asyncio
from pyautogui import press

class InputRequest:
    def __init__(self, prompt, desc='', hint='', default=None, password=False, prevalue=''):
        self.prompt = prompt
        self.desc = desc
        self.hint = hint
        self.default = default
        self.password = password
        self.prevalue = prevalue
        
class Scene:
    def __init__(self, items, main_prompt='Select what you want', help_prompt='Show Help Doc', help_title='', help_doc='', cursor=0, multi_select=False) -> None:
        self.main_prompt = main_prompt
        self.help_prompt = help_prompt
        self.help_title = help_title
        self.help_doc = help_doc
        self.multi_select = multi_select
        self.cursor = cursor
        self.items = [CheckableListItem(item, show_checkbox=multi_select) for item in items]
    
class CustomProcess:
    def __init__(self, app) -> None:
        self.app = app
        self.__received_input_value = None
        self.__received_select_items = None
        self.__abort_input_flag = False
        self.__abort_select_flag = False
        self.is_waiting_input = False
        self.is_waiting_select = False
        self.is_running = False
        
    async def main(self): pass    
        
    async def __run(self):
        try:
            while True: 
                try: await self.main()
                except self.InputAborted: self.app.clear_input()
        except self.Return as ret:
            return ret.value
        
    def run(self):
        if not self.is_running:
            asyncio.ensure_future(self.__run())

    def response_input(self, value:str):
        self.__received_input_value = value
        
    def response_select(self, items:dict):
        self.__received_select_items = items
        
    def abort_input(self):
        self.__abort_input_flag = True
        
    def abort_select(self):
        self.__abort_select_flag = True
        
    def exit(self, value):
        raise self.Return(value)
    
    async def request_input(self, input_request:InputRequest, polling_rate=0.05):
        #set input layout and open container
        asyncio.ensure_future(self.app.set_input(input_request))
        self.app.open_input()
                
        #wait until user input
        self.is_waiting_input = True
        while self.__received_input_value == None:
            
            #check aborted
            if self.__abort_input_flag == True:
                self.__abort_input_flag = False
                self.is_waiting_input = False
                raise self.InputAborted
            
            await asyncio.sleep(polling_rate)
        
        #make return
        ret = self.__received_input_value
        self.__received_input_value = None
        self.is_waiting_input = False
        
        return ret
    
    async def request_select(self, scene, polling_rate=0.05):
        #update TUI with given scene
        self.app.main_screen.list_container.push_list_from_scene(scene)
        
        # await self.app.set_scene(scene)
        
        #wait until user select or submit
        self.is_waiting_select = True
        while self.__received_select_items == None:
            
            #check aborted
            if self.__abort_select_flag == True:
                self.__abort_select_flag = False
                self.is_waiting_select = False
                self.exit(None)
            
            await asyncio.sleep(polling_rate)
            
        #make return
        ret = self.__received_select_items
        self.__received_select_items = None
        self.is_waiting_select = False
    
        return ret
    
    class InputAborted(Exception): pass
    class Return(Exception): 
        def __init__(self, value):
            super().__init__()
            self.value = value
    
    
        
    