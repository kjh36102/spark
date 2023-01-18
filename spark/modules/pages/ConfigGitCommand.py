import sys
sys.path.append('./spark/modules/')
sys.path.append('./spark/modules/pages/')

from TUI import CustomProcess, TUIApp
from TUI_DAO import Scene, InputRequest, get_func_names

import os

class ConfigGitCommandProcess(CustomProcess):
    def __init__(self, app: 'TUIApp') -> None:
        super().__init__(app)
        
        self.funcs = [
            self.See_git_command,
            self.Reconfigure,
        ]
        
        func_names = get_func_names(self.funcs)
        
        self.scene = Scene(
            main_prompt='Config Git Command',
            items=func_names
        )
        
    async def main(self):
        idx, val = await self.request_select(self.scene)
        await self.funcs[idx]()
    
    async def See_git_command(self):
        await see_git_command(self, self.app)
    
    async def Reconfigure(self):
        await reconfigure(self, self.app)
        
#---------------------------------------------------------------------

async def see_git_command(process:CustomProcess, app:TUIApp):
    cmd_line = load_git_command()
    app.alert(cmd_line)

async def reconfigure(process:CustomProcess, app:TUIApp):
    
    prev_cmd = load_git_command()
    
    cmd_line = await process.request_input(
        InputRequest(
            prompt='Type git commit and push command',
            help_doc="Type git commands seperated with semicolons(;) which execute automatically when select 'Compile and Push' in main menu. Leave blank for setting default commands which pushing master to origin. ex) git add *; git status; git commit -m 'blah blah';",
            hint='sequence of git commands ending in semicolons(;)',
            default='git add *; git commit -m "Auto pushed by spark"; git push origin master;',
            prevalue=prev_cmd
        )
    )
    
    f_git_cmd = open('spark/git_cmd.txt', 'w')
    f_git_cmd.write(cmd_line)
    f_git_cmd.close()

    app.alert(f'Your git command has been saved in git_cmd.txt')
    
    
def load_git_command():
    file_path = './spark/git_cmd.txt'

    #return empty string if file not exist
    if not os.path.isfile(file_path):
        return ''
    else:
        f = open(file_path, 'r', encoding='utf-8')
        raw_info = f.read()
        f.close()

        return raw_info