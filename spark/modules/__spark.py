
from TUI import *
from TUI_DAO import get_func_names

# from pages import ManageCategory
# from pages import ManagePost
from pages import ConfigFTPInfo
from pages import AdvancedMenu
from pages import ManageCategory
from pages import ManagePost
from pages import ConfigGitCommand
    
class Main(CustomProcess):
    def __init__(self, app: 'TUIApp', *args) -> None:
        super().__init__(app, *args)

        self.funcs = [
            self.Create_new_post,
            self.Compile_and_push,
            self.Advanced_menu,
            self.Manage_post,
            self.Manage_category,
            self.Config_ftp_info,
            self.Config_git_command,
            self.Config_blog_info,
            self.Initialize_blog,
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
    
    async def Create_new_post(self): 
        await asyncio.create_task(ManagePost.create_post(self, self.app))
    
    async def Advanced_menu(self):
        await self.run_next_process(AdvancedMenu.AdvancedMenuProcess(self.app))
    
    async def Compile_and_push(self): 
        await asyncio.create_task(AdvancedMenu.compile_and_push(self, self.app))
    
    async def Manage_post(self): 
        await self.run_next_process(ManagePost.ManagePostProcess(self.app))
    
    async def Manage_category(self): 
        await self.run_next_process(ManageCategory.ManageCategoryProcess(self.app))
    
    async def Config_git_command(self): 
        await self.run_next_process(ConfigGitCommand.ConfigGitCommandProcess(self.app))
    
    async def Config_blog_info(self): pass
    
    async def Config_ftp_info(self):
        await self.run_next_process(ConfigFTPInfo.ConfigFTPInfoProcess(self.app))
    
    async def Initialize_blog(self):
        pass
    
class Spark(TUIApp):
    def __init__(self):
        super().__init__()
        
    def on_ready(self):
        Main(self).run()

spark = Spark()
spark.run()

