import sys
sys.path.append('./spark/modules/')
sys.path.append('./spark/pages/')

from TUI import TUIApp
from TUI_DAO import  get_func_names
from TUI_events import CustomProcess, Scene, InputRequest
from TUI_Widgets import CheckableListItem

from pages import ManageCategory
from pages import ManagePost
from pages import ConfigFTPInfo
    
class Main(CustomProcess):
    def __init__(self, app: 'TUIApp', *args) -> None:
        super().__init__(app, *args)

        self.funcs = [
            self.create_new_post,
            self.commit_and_push,
            self.advanced_menu,
            self.manage_post,
            self.manage_category,
            self.config_ftp_info,
            self.config_git_info,
            self.config_blog_info,
            self.initialize_blog,
        ]
        
        help_doc ='''\
create new post - Create new post automatically.
synchronize post - Synchronize post with FTP server.
commit & push - commit and push to github.
manage post - Managing settings about specific post.
manage category - Managing your categories.
convert image URL - Change local image URL to embeded URL from FTP server.
revert image URL -  Change embeded URL to local image URL.
config FTP info - Config FTP info for using synchronize feature.
change CSS theme - Change blog css theme.
initialize blog - After clone from github, must run this once.\
'''     
        func_names = get_func_names(self.funcs)
        
        self.main_scene = Scene(
            items=func_names,
            main_prompt = 'Welcome to Spark!',
            help_title='Index description',
            help_doc=help_doc,
        )
    
    async def main(self):
        idx, val = await self.request_select(self.main_scene)
        
        await self.funcs[idx]()
        
        pass
    
    async def create_new_post(self): 
        idx, val = await self.request_input(InputRequest(
            prompt='asdf',
            desc='qwer',
            hint='zxcv',
            default='zz'
        ))
        
        pass
    
    async def advanced_menu(self): pass
    
    async def commit_and_push(self): pass
    
    async def manage_post(self): pass
    
    async def manage_category(self): pass
    
    async def config_git_info(self): pass
    
    async def config_blog_info(self): pass
    
    async def config_ftp_info(self):
        self.app.print_log('before run')
        self.app.run_custom_process(ConfigFTPInfo.ConfigFTPInfoProcess(self), child=False)
    
    async def initialize_blog(self): pass
    
class Spark(TUIApp):
    def __init__(self):
        super().__init__()
        
    def on_ready(self):
        self.run_custom_process(Main(self))

if __name__ == '__main__':
    spark = Spark()
    spark.run()
    