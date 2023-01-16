from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from TUI import TUIApp, ListContainer

from TUI import TUIApp, ListContainer
from TUI import ListView
from TUI_Widgets import CheckableListItem

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
        self.list_view = None
        self.selected_items = {}
        
class CustomProcess:
    def __init__(self, app:TUIApp) -> None:
        self.app = app
        self.scene_stack = []
        self.parent = None
        self.__received_input_value = None
        self.__received_select_items = None
        self.__process_return = None
        self.__abort_input_flag = False
        self.__abort_select_flag = False
        self.__abort_process_flag = False
        self.is_waiting_input = False
        self.is_waiting_select = False
        self.is_running = False
    
    async def run_next_process(self, process:CustomProcess, polling_interval=0.05):
        
        #run next process and get result
        ret = await process.__run(parent=self)
        
        #get list contaier
        list_container:ListContainer = self.app.main_screen.list_container
        
        #remove remain list
        list_container.target_scene.list_view.remove()
        
        #restore scene
        list_container.target_scene = self.scene_stack[-1]
        
        #make list visible
        list_container.target_scene.list_view.styles.display = 'block'
        
        #restore focus
        self.app.set_focus(list_container.target_scene.list_view)
        
        #restore process target
        self.app.target_process = self
        
        return ret
    
    def push_scene(self, scene:Scene):
        #get list container
        list_container:ListContainer = self.app.main_screen.list_container
        
        #if there is any context
        if len(self.scene_stack) > 0:
            last_scene = self.scene_stack[-1]
                        
            # exit when last scene is new scene
            if last_scene is scene : return
            
            #make unvisible last list
            last_scene.list_view.styles.display = 'none'
        
        #if ther isn't any contents, or new process start
        else:
            #vanish previous process's scene
            if list_container.target_scene != None:
                list_container.target_scene.list_view.styles.display = 'none'            
            pass
            
        #add new list to list container
        scene.list_view = ListView(*scene.items)
        list_container.mount(scene.list_view)
        
        #add new scene to stack
        self.scene_stack.append(scene)
        
        #set current scene to target
        list_container.target_scene = scene    
        
        
    def pop_scene(self):
        
        if len(self.scene_stack) > 1:
            # get upper scene
            upper_scene:Scene = self.scene_stack[-2]
            
            #make upper list visible
            upper_scene.list_view.styles.display = 'block'
            
            #restore previous cursor
            self.app.set_focus(upper_scene.list_view)
            upper_scene.list_view.index = upper_scene.cursor
            
            #get last scene
            last_scene:Scene = self.scene_stack[-1]
            
            #remove last list from dom
            last_scene.list_view.remove()
            
            #remove last scene from stack
            self.scene_stack.pop()
            
            #set current scene to target
            self.app.main_screen.list_container.target_scene = upper_scene
            
        elif len(self.scene_stack) == 1:
            if self.parent != None: self.exit()
    
    async def main(self):
        '''override this'''
        pass    
    
    def print_status(self, title='No tile'):
        class_name = self.__class__.__name__
        
        current_statue = f'''\
 [{title}]
class name: {class_name}
  parent: {self.parent.__class__.__name__}
  __received_input_value: {self.__received_input_value}
  __received_select_items: {self.__received_select_items}
  __process_return: {self.__process_return}
  __abort_input_flag: {self.__abort_input_flag}
  __abort_select_flag: {self.__abort_select_flag}
  __abort_process_flag: {self.__abort_process_flag}
  is_waiting_input: {self.is_waiting_input}
  is_waiting_select: {self.is_waiting_select}
  is_running: {self.is_running}
  scene_stack: {self.scene_stack}\
'''
        self.app.print_log(current_statue)
        
    
    async def __run(self, parent=None):
        self.parent = parent
        self.app.target_process = self
        
        while True: 
            if self.__abort_process_flag:
                return self.__process_return
            try: await self.main()
            except self.InputAborted: self.app.clear_input()
            except self.SelectAborted: self.pop_scene()
        
    def run(self):
        # if not self.is_running:
        asyncio.ensure_future(self.__run())

    def response_input(self, value:str):
        self.__received_input_value = value
        self.app.clear_input()
        
    def response_select(self, items:dict):
        self.__received_select_items = items
        
    def abort_input(self):
        self.__abort_input_flag = True
        
    def abort_select(self):
        self.__abort_select_flag = True
        
        self.pop_scene()
        
        
        
    def exit(self, value=None):
        self.__abort_process_flag = True
        self.__process_return = value
        
    
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
        self.push_scene(scene)
        
        #wait until user select or submit
        self.is_waiting_select = True
        while self.__received_select_items == None:
            
            #check aborted
            if self.__abort_select_flag == True:
                self.__abort_select_flag = False
                self.is_waiting_select = False
                raise self.SelectAborted
            
            await asyncio.sleep(polling_rate)
            
        #make return
        ret = self.__received_select_items
        self.__received_select_items = None
        self.is_waiting_select = False
        
        self.pop_scene()
    
        return ret
    
    class InputAborted(Exception): pass
    class SelectAborted(Exception): pass
    
        
    