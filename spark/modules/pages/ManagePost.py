import sys
sys.path.append('./spark/modules/')
sys.path.append('./spark/pages/')

from TUI import TUIApp
from TUI_DAO import Scene, get_func_names, InputRequest
from TUI_Widgets import CheckableListItem
from TUI_events import CustomProcess

from pages import ManageCategory

import os
from datetime import datetime

class ManagePostProcess(CustomProcess):
    def __init__(self, app: 'TUIApp', *args) -> None:
        super().__init__(app, *args)
        
        self.funcs = [
            ManagePostProcess.create_post,
            ManagePostProcess.rename_post,
            ManagePostProcess.delete_post,
            ManagePostProcess.move_post,
            ManagePostProcess.timestamp_post
        ]
    
        func_names = get_func_names(self.funcs)
    
        self.scene = Scene(
            main_prompt='Manage Post',
            items=[CheckableListItem(func_name) for func_name in func_names]
        )
        
    async def main(self):
        while True:
            idx, val = await self.request_select(self.scene)
            await self.run(self.funcs[idx])
        
        return await super().main()
    
    async def create_post(process, app):
        await create_post(process, app)
    
    async def rename_post(process, app):
        pass
    
    async def delete_post(process, app):
        await delete_post(process, app)
    
    async def move_post(process, app):
        pass
    
    async def timestamp_post(process, app):
        pass

#-----------------------------------------------------------------





async def create_post(process:CustomProcess, app:TUIApp):
    while True:
        try:
            # category_scene = ManageCategory.get_category_select_scene(prompt='Create Post')

            # if category_scene == None: 
            #     app.alert('You have not created any categories yet.', 'Error') 
            #     return
            
            # idx, selected_category = await process.request_select(category_scene)
            
            selected_category = await process.request_from_child(ManageCategory.CategorySelector(app, 'Create Post'))
            app.print_log('selected category zz:', selected_category)
            
            
            post_title = await process.request_input(
                InputRequest(
                    prompt="New Post Title",
                    help_doc="Enter the title of the new post.",
                    hint="new post title",
                    essential=True,
                )
            )
            
            post_comments = await process.request_input(
                InputRequest(
                    prompt='Use Comments?',
                    help_doc='Do you want to use Disqus comments in your post? Default: y',
                    hint='y or n',
                    default='y',
                )
            )
            
            post_tags = await process.request_input(
                InputRequest(
                    prompt='Tags',
                    help_doc='Type tag list seperated with comma(,). ex) IT, Python, Blogging',
                    hint='tags with comma',
                    default=''
                )
            )
            
            break
        except process.AbortedException: pass
        finally: app.clear_input_box()
    
        # base파일 불러오기
        f = open('./spark/post_base.md', 'r', encoding='utf-8')
        base_raw = ''.join(f.readlines())
        f.close()

        #base파일 변형하기
        base_raw = base_raw.replace('post_title', post_title)
        base_raw = base_raw.replace('post_comments', 'false' if post_comments == 'n' else 'true')
        base_raw = base_raw.replace('post_categories', selected_category)
        base_raw = base_raw.replace('post_tags', post_tags)
        base_raw = base_raw.replace('post_contents', f'generated at {datetime.now()}')

        #category폴더에 파일 생성하기
        post_dir = f'./_posts/{selected_category}/{post_title}'
        post_file_path = f'{post_dir}/{post_title}.md'
        os.makedirs(post_dir, exist_ok=True)
        f = open(post_file_path, 'w', encoding='utf-8')
        f.write(base_raw)
        
        #uncompiled_path.txt 없다면 생성하고, 경로 추가하기
        f = open('./spark/uncompiled_path.txt', 'a+', encoding='utf-8')
        f.write(post_file_path + '\n')
        f.close()

        app.alert(f'Succefully created new post: {post_file_path}')



async def rename_post(process:CustomProcess, app:TUIApp):
    pass



async def delete_post(process:CustomProcess, app:TUIApp):
    
    while True:
        category_scene = ManageCategory.get_category_select_scene('Delete Post')
        
        if category_scene == None: 
            app.alert('You have not created any categories yet.', 'Error')
            return
        
        #카테고리 이름 가져오기
        category_name = await process.request_select(category_scene)
        
        #카테고리 내부 포스트 목록 씬 가져오기
        post_list_scene = get_post_list_scene('Delete Post', category_name)
        
        if post_list_scene == None:
            app.alert(f"You haven't created any posts yet in this category:{category_name}")
            return
        
        #선택한 포스트 이름 가져오기
        selected_post_name = await process.request_select(post_list_scene)
        
        app.print_log('selected post name:', selected_post_name)
            

            
            
            





async def move_post(process:CustomProcess, app:TUIApp):
    pass









async def timestamp_post(process:CustomProcess, app:TUIApp):
    pass









def get_post_list_scene(prompt, category_name):
    
    #get post name list of given category name
    category_path = f'./_posts/{category_name}/'
    
    post_list = os.listdir(category_path)
    
    if len(post_list) == 0: return None
    
    scene = Scene(
        main_prompt=f'{prompt} - Select Post',
        items=[CheckableListItem(post_name) for post_name in post_list]
    )
    
    return scene


# def create_post(app:TUIApp, item:CheckableListItem):
    
    
#     # class CreateNewPostProcess(CustomProcess):
#     #     def __init__(self, app: TUIApp, *args): super().__init__(app, *args)
#     #     async def main(self):
#     #         category_name = self.args[0]
            
#     #         post_title = await self.request_input(
#     #             InputRequest(prompt="Type new post's title", hint="new post's title", essential=True))
            
#     #         post_comments = await self.request_input(
#     #             InputRequest(prompt='Use comments?', help_doc="default: y", hint='y or n'))
            
#     #         post_tags =  await self.request_input(
#     #             InputRequest(
#     #                 prompt='Type tage list',
#     #                 help_doc='Type tag list seperated with comma(,). ex) IT, Python, Blogging',
#     #                 hint='tags with comma'
#     #                 )
#     #         )
            
#     #         #base파일 불러오기
#     #         f = open('./spark/post_base.md', 'r', encoding='utf-8')
#     #         base_raw = ''.join(f.readlines())
#     #         f.close()

#     #         #base파일 변형하기
#     #         base_raw = base_raw.replace('post_title', post_title)
#     #         base_raw = base_raw.replace('post_comments', 'false' if post_comments == 'n' else 'true')
#     #         base_raw = base_raw.replace('post_categories', category_name)
#     #         base_raw = base_raw.replace('post_tags', post_tags)
#     #         base_raw = base_raw.replace('post_contents', f'generated at {datetime.now()}')

#     #         #category폴더에 파일 생성하기
#     #         post_dir = f'./_posts/{category_name}/{post_title}'
#     #         post_file_path = f'{post_dir}/{post_title}.md'
#     #         os.makedirs(post_dir, exist_ok=True)
#     #         f = open(post_file_path, 'w', encoding='utf-8')
#     #         f.write(base_raw)
            
#     #         #uncompiled_path.txt 없다면 생성하고, 경로 추가하기
#     #         f = open('./spark/uncompiled_path.txt', 'a+', encoding='utf-8')
#     #         f.write(post_file_path + '\n')
#     #         f.close()

#     #         app.alert(f'Succefully created new post: {post_file_path}')
            
#     #         return await super().main()
    
#     # def callback(app:TUIApp, item:CheckableListItem):
#     #     selected_category = item.value
#     #     app.run_custom_process(CreateNewPostProcess(app, selected_category))
    
#     # scene = get_category_list_scene(
#     #     prompt='Create Post - Select Category',
#     #     callback=callback,
#     #     multi_select=False,
#     # )
    
#     # #if there is no category
#     # if scene == None:
#     #     app.alert('You have not created any categories yet.', prompt='Error!')
#     # else: app.push_scene(scene)
#     pass

# def rename_post(app:TUIApp, item:CheckableListItem):
#     # class CreateNewPostProcess(CustomProcess):
#     #     def __init__(self, app: TUIApp, *args): super().__init__(app, *args)
#     #     async def main(self):
#     #         category_name = self.args[0]
            
#     #         post_title = await self.request_input(
#     #             InputRequest(prompt="Type new post's title", hint="new post's title", essential=True))
            
#     #         post_comments = await self.request_input(
#     #             InputRequest(prompt='Use comments?', help_doc="default: y", hint='y or n'))
            
#     #         post_tags =  await self.request_input(
#     #             InputRequest(
#     #                 prompt='Type tage list',
#     #                 help_doc='Type tag list seperated with comma(,). ex) IT, Python, Blogging',
#     #                 hint='tags with comma'
#     #                 )
#     #         )
            
#     #         #base파일 불러오기
#     #         f = open('./spark/post_base.md', 'r', encoding='utf-8')
#     #         base_raw = ''.join(f.readlines())
#     #         f.close()

#     #         #base파일 변형하기
#     #         base_raw = base_raw.replace('post_title', post_title)
#     #         base_raw = base_raw.replace('post_comments', 'false' if post_comments == 'n' else 'true')
#     #         base_raw = base_raw.replace('post_categories', category_name)
#     #         base_raw = base_raw.replace('post_tags', post_tags)
#     #         base_raw = base_raw.replace('post_contents', f'generated at {datetime.now()}')

#     #         #category폴더에 파일 생성하기
#     #         post_dir = f'./_posts/{category_name}/{post_title}'
#     #         post_file_path = f'{post_dir}/{post_title}.md'
#     #         os.makedirs(post_dir, exist_ok=True)
#     #         f = open(post_file_path, 'w', encoding='utf-8')
#     #         f.write(base_raw)
            
#     #         #uncompiled_path.txt 없다면 생성하고, 경로 추가하기
#     #         f = open('./spark/uncompiled_path.txt', 'a+', encoding='utf-8')
#     #         f.write(post_file_path + '\n')
#     #         f.close()

#     #         app.alert(f'Succefully created new post: {post_file_path}')
            
#     #         return await super().main()
    
#     # def callback(app:TUIApp, item:CheckableListItem):
#     #     selected_category = item.value
#     #     app.run_custom_process(CreateNewPostProcess(app, selected_category))
    
#     # scene = get_category_list_scene(
#     #     prompt='Rename Post - Select Category',
#     #     callback=callback,
#     #     multi_select=False,
#     # )
    
#     # #if there is no category
#     # if scene == None:
#     #     app.alert('You have not created any categories yet.', prompt='Error!')
#     # else: app.push_scene(scene)
#     pass

# def delete_post(app:TUIApp, item:CheckableListItem):
    
#     class DeletePostProcess(CustomProcess):
#         def __init__(self, app: 'TUIApp', *args) -> None: super().__init__(app, *args)
#         async def main(self):
#             # delete post dir and files it's inside
            
#             # search
            
#             return await super().main()
    
#     def callback(app:TUIApp, item:CheckableListItem):
#         scene = get_post_list_scene(app, item, category_name=item.value)
#         app.push_scene(scene)
        
#         pass
    
#     if not request_get_category(app, 'Delete Post', callback): return

# def move_post(app:TUIApp, item:CheckableListItem):
#     pass

