import sys
sys.path.append('./spark/modules/')
sys.path.append('./spark/modules/pages/')

from TUI import TUIApp
from TUI_DAO import Scene, get_func_names, InputRequest
from TUI_Widgets import CheckableListItem
from TUI_events import CustomProcess

from pages import ManageCategory
from ManageCategory import get_category_list_scene

from datetime import datetime
import os

def get_scene():

    funcs = [
            create_new_post,
            synchronize_post,
            commit_and_push,
            manage_post,
            manage_category,
            convert_image_url,
            revert_image_url,
            config_ftp_info,
            change_css_theme,
            initialize_blog,
    ]

    help ='''\
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

    func_names = get_func_names(funcs)

    scene = Scene(
        main_prompt='Welcome to Spark!',
        items=[CheckableListItem(value=func_name, callback=func, show_checkbox=False) for func_name, func in zip(func_names, funcs)],
        help_title='Index description',
        help_doc=help
    )

    return scene

def create_new_post(app:TUIApp, item:CheckableListItem):
    
    class CreateNewPostProcess(CustomProcess):
        def __init__(self, app: TUIApp, *args): super().__init__(app, *args)
        async def main(self):
            category_name = self.args[0]
            
            post_title = await self.request_input(
                InputRequest(prompt="Type new post's title", hint="new post's title", essential=True))
            
            post_comments = await self.request_input(
                InputRequest(prompt='Use comments?', help_doc="default: y", hint='y or n'))
            
            post_tags =  await self.request_input(
                InputRequest(
                    prompt='Type tage list',
                    help_doc='Type tag list seperated with comma(,). ex) IT, Python, Blogging',
                    hint='tags with comma'
                    )
            )
            
            #base파일 불러오기
            f = open('./spark/post_base.md', 'r', encoding='utf-8')
            base_raw = ''.join(f.readlines())
            f.close()

            #base파일 변형하기
            base_raw = base_raw.replace('post_title', post_title)
            base_raw = base_raw.replace('post_comments', 'false' if post_comments == 'n' else 'true')
            base_raw = base_raw.replace('post_categories', category_name)
            base_raw = base_raw.replace('post_tags', post_tags)
            base_raw = base_raw.replace('post_contents', f'generated at {datetime.now()}')

            #category폴더에 파일 생성하기
            post_dir = f'./_posts/{category_name}/{post_title}'
            post_file_path = f'{post_dir}/{post_title}.md'
            os.makedirs(post_dir, exist_ok=True)
            f = open(post_file_path, 'w', encoding='utf-8')
            f.write(base_raw)

            app.alert(f'Succefully created new post: {post_file_path}')
            
            return await super().main()
    
    def callback(app:TUIApp, item:CheckableListItem):
        selected_category = item.value
        app.run_custom_process(CreateNewPostProcess(app, selected_category))
    
    scene = get_category_list_scene(
        prompt='Which category do you want to create in?',
        callback=callback,
        multi_select=False,
    )
    
    #if there is no category
    if scene == None:
        app.alert('You have not created any categories yet.', prompt='Error!')
        pass
    else: app.push_scene(scene)

def synchronize_post(spark):
    pass

def commit_and_push(spark):
    pass

def manage_post(spark):
    pass

def manage_category(app:TUIApp, item:CheckableListItem):
    app.push_scene(ManageCategory.get_scene())
    pass

def convert_image_url(spark):
    pass

def revert_image_url(spark):
    pass

def config_ftp_info(spark:TUIApp):
    pass

def change_css_theme(spark):
    pass

def initialize_blog(spark):
    pass