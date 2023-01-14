import sys
sys.path.append('./spark/modules/')
sys.path.append('./spark/pages/')

from TUI import TUIApp
from TUI_DAO import Scene, InputRequest, get_func_names
from TUI_events import CustomProcess
from TUI_Widgets import CheckableListItem

from pages import ManageCategory
    
class Main(CustomProcess):
    def __init__(self, app: 'TUIApp', *args) -> None:
        super().__init__(app, *args)

        self.funcs = [
            self.create_new_post,
            self.synchronize_post,
            self.commit_and_push,
            self.manage_post,
            self.manage_category,
            self.convert_image_url,
            self.revert_image_url,
            self.config_ftp_info,
            self.change_css_theme,
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
            main_prompt = 'Welcome to Spark!',
            items=[CheckableListItem(func_name) for func_name in func_names],
            help_title='Index description',
            help_doc=help_doc
        )
        
    async def main(self):
        while True:
            idx, val = await self.request_select(self.main_scene)
            
            await self.funcs[idx]()
            
        return await super().main()
    
    async def create_new_post(self): 
        await ManageCategory.create_category(self, self.app)
    
    async def synchronize_post(self): pass
    
    async def commit_and_push(self): pass
    
    async def manage_post(self): pass
    
    async def manage_category(self): 
        self.app.run_custom_process(ManageCategory.ManageCategoryProcess(self.app))
    
    async def convert_image_url(self): pass
    
    async def revert_image_url(self): pass
    
    async def config_ftp_info(self): pass
    
    async def change_css_theme(self): pass
    
    async def initialize_blog(self): pass
    
    
    
class Spark(TUIApp):
    def __init__(self):
        super().__init__()
        
    def on_ready(self):
        self.run_custom_process(Main(self))

if __name__ == '__main__':
    spark = Spark()
    spark.run()