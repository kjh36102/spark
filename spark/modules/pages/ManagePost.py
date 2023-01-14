import sys
sys.path.append('./spark/modules/')

from TUI import TUIApp
from TUI_DAO import Scene, get_func_names, InputRequest
from TUI_Widgets import CheckableListItem
from TUI_events import CustomProcess

from ManageCategory import request_get_category

import os
import datetime

def get_scene():
    funcs = [
        create_post,
        rename_post,
        delete_post,
        move_post,
    ]
    
    func_names = get_func_names(funcs)
    
    scene = Scene(
        main_prompt='Manage Post',
        items=[(CheckableListItem(func_name, func, show_checkbox=False))for func_name, func in zip(func_names, funcs)]
    )
    
    return scene

def create_post(app:TUIApp, item:CheckableListItem):
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
            
            #uncompiled_path.txt 없다면 생성하고, 경로 추가하기
            f = open('./spark/uncompiled_path.txt', 'a+', encoding='utf-8')
            f.write(post_file_path + '\n')
            f.close()

            app.alert(f'Succefully created new post: {post_file_path}')
            
            return await super().main()
    
    def callback(app:TUIApp, item:CheckableListItem):
        selected_category = item.value
        app.run_custom_process(CreateNewPostProcess(app, selected_category))
    
    scene = get_category_list_scene(
        prompt='Create Post - Select Category',
        callback=callback,
        multi_select=False,
    )
    
    #if there is no category
    if scene == None:
        app.alert('You have not created any categories yet.', prompt='Error!')
    else: app.push_scene(scene)
    pass

def rename_post(app:TUIApp, item:CheckableListItem):
    # class CreateNewPostProcess(CustomProcess):
    #     def __init__(self, app: TUIApp, *args): super().__init__(app, *args)
    #     async def main(self):
    #         category_name = self.args[0]
            
    #         post_title = await self.request_input(
    #             InputRequest(prompt="Type new post's title", hint="new post's title", essential=True))
            
    #         post_comments = await self.request_input(
    #             InputRequest(prompt='Use comments?', help_doc="default: y", hint='y or n'))
            
    #         post_tags =  await self.request_input(
    #             InputRequest(
    #                 prompt='Type tage list',
    #                 help_doc='Type tag list seperated with comma(,). ex) IT, Python, Blogging',
    #                 hint='tags with comma'
    #                 )
    #         )
            
    #         #base파일 불러오기
    #         f = open('./spark/post_base.md', 'r', encoding='utf-8')
    #         base_raw = ''.join(f.readlines())
    #         f.close()

    #         #base파일 변형하기
    #         base_raw = base_raw.replace('post_title', post_title)
    #         base_raw = base_raw.replace('post_comments', 'false' if post_comments == 'n' else 'true')
    #         base_raw = base_raw.replace('post_categories', category_name)
    #         base_raw = base_raw.replace('post_tags', post_tags)
    #         base_raw = base_raw.replace('post_contents', f'generated at {datetime.now()}')

    #         #category폴더에 파일 생성하기
    #         post_dir = f'./_posts/{category_name}/{post_title}'
    #         post_file_path = f'{post_dir}/{post_title}.md'
    #         os.makedirs(post_dir, exist_ok=True)
    #         f = open(post_file_path, 'w', encoding='utf-8')
    #         f.write(base_raw)
            
    #         #uncompiled_path.txt 없다면 생성하고, 경로 추가하기
    #         f = open('./spark/uncompiled_path.txt', 'a+', encoding='utf-8')
    #         f.write(post_file_path + '\n')
    #         f.close()

    #         app.alert(f'Succefully created new post: {post_file_path}')
            
    #         return await super().main()
    
    # def callback(app:TUIApp, item:CheckableListItem):
    #     selected_category = item.value
    #     app.run_custom_process(CreateNewPostProcess(app, selected_category))
    
    # scene = get_category_list_scene(
    #     prompt='Rename Post - Select Category',
    #     callback=callback,
    #     multi_select=False,
    # )
    
    # #if there is no category
    # if scene == None:
    #     app.alert('You have not created any categories yet.', prompt='Error!')
    # else: app.push_scene(scene)
    pass

def delete_post(app:TUIApp, item:CheckableListItem):
    
    class DeletePostProcess(CustomProcess):
        def __init__(self, app: 'TUIApp', *args) -> None: super().__init__(app, *args)
        async def main(self):
            # delete post dir and files it's inside
            
            # search
            
            return await super().main()
    
    def callback(app:TUIApp, item:CheckableListItem):
        scene = get_post_list_scene(app, item, category_name=item.value)
        app.push_scene(scene)
        
        pass
    
    if not request_get_category(app, 'Delete Post', callback): return

def move_post(app:TUIApp, item:CheckableListItem):
    pass

def get_post_list_scene(app:TUIApp, item:CheckableListItem, category_name):
    
    #get post name list of given category name
    category_path = f'./_posts/{category_name}/'
    
    post_list =  os.listdir(category_path)
    
    scene = Scene(
        main_prompt='Which post do you want to delete?',
        items=[CheckableListItem(post_name) for post_name in post_list]
    )
    
    return scene