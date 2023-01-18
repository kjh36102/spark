
from TUI import *
from TUI_DAO import get_func_names

# from pages import ManageCategory
# from pages import ManagePost
from pages import ConfigFTPInfo
from pages import AdvancedMenu
from pages import ManageCategory
from pages import ManagePost
    
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
    
    async def create_new_post(self): 
        await asyncio.create_task(ManagePost.create_post(self, self.app))
    
    async def advanced_menu(self):
        await self.run_next_process(AdvancedMenu.AdvancedMenuProcess(self.app))
    
    async def commit_and_push(self): pass
    
    async def manage_post(self): 
        await self.run_next_process(ManagePost.ManagePostProcess(self.app))
        pass
    
    async def manage_category(self): 
        await self.run_next_process(ManageCategory.ManageCategoryProcess(self.app))
        pass
    
    async def config_git_info(self): pass
    
    async def config_blog_info(self): pass
    
    async def config_ftp_info(self):
        await self.run_next_process(ConfigFTPInfo.ConfigFTPInfoProcess(self.app))
    
    async def initialize_blog(self):
        pass
    
class Spark(TUIApp):
    def __init__(self):
        super().__init__()
        
    def on_ready(self):
        Main(self).run()

spark = Spark()
spark.run()

