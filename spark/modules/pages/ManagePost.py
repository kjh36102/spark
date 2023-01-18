import sys
sys.path.append('./spark/modules/')
sys.path.append('./spark/modules/pages/')

from TUI import *
from TUI_DAO import *
from TUI_Widgets import CheckableListItem

from pages import ManageCategory


import re
import os
import shutil
from datetime import datetime

class ManagePostProcess(CustomProcess):
    def __init__(self, app: 'TUIApp') -> None:
        super().__init__(app)
        
        self.funcs = [
            self.Create_post,
            self.Rename_post,
            self.Delete_post,
            self.Move_post,
            self.Timestamp_post
        ]
    
        func_names = get_func_names(self.funcs)
    
        self.scene = Scene(
            main_prompt='Manage Post',
            items=func_names
        )
        
    async def main(self):
        idx, val = await self.request_select(self.scene)
        await self.funcs[idx]()

    async def Create_post(self): 
        await asyncio.create_task(create_post(self, self.app))
    async def Rename_post(self): 
        await asyncio.create_task(rename_post(self, self.app))
    async def Delete_post(self): 
        await asyncio.create_task(delete_post(self, self.app))
    async def Move_post(self): 
        await asyncio.create_task(move_post(self, self.app))
    async def Timestamp_post(self): 
        await asyncio.create_task(timestamp_post(self, self.app))

#-----------------------------------------------------------------

async def create_post(process:CustomProcess, app:TUIApp):
    app.print('In create post')
    #get category scene
    category_scene = ManageCategory.get_category_select_scene(prompt='Create Post')

    #if there is no category
    if category_scene == None:
        app.alert("You haven't created any categories yet.")
        return

    app.print('before request select')

    _, selected_category = await process.request_select(category_scene)
    
    app.print('after request select')

    post_title = await process.request_input(
        InputRequest(
            prompt=f"{selected_category} - New Post Title",
            help_doc="Enter the title of the new post.",
            hint="new post title",
            essential=True,
        )
    )
    
    post_comments = await process.request_input(
        InputRequest(
            prompt=f'{selected_category} - Use Comments?',
            help_doc='Do you want to use Disqus comments in your post? Default: y',
            hint='y or n',
            default='y',
        )
    )
    
    post_tags = await process.request_input(
        InputRequest(
            prompt=f'{selected_category} - Tags',
            help_doc='Type tag list seperated with comma(,). ex) IT, Python, Blogging',
            hint='tags with comma',
            default=''
        )
    )

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
    category_scene = ManageCategory.get_category_select_scene('Rename Post')
    
    if category_scene == None: 
        app.alert('You have not created any categories yet.', 'Error')
        return
    
    #카테고리 이름 가져오기
    _, category_name = await process.request_select(category_scene)
    
    #카테고리 내부 포스트 목록 씬 가져오기
    post_list_scene = get_post_list_scene(category_name, prompt='Rename Post', multi_select=False)
    
    if post_list_scene == None:
        app.alert(f"You haven't created any posts yet in this category:{category_name}")
        return
    
    #선택한 포스트 이름 가져오기
    idx, selected_post_name = await process.request_select(post_list_scene)
    
    #컴파일된 포스팅인지 확인하기
    compiled_re = re.compile(r'(\d{4}-\d{2}-\d{2})-(.*)')
    compile_flag = bool(compiled_re.match(selected_post_name))
    
    #입력요청 띄우기
    new_post_name = await process.request_input(
        InputRequest(
            prompt=f'Rename {category_name}/{selected_post_name}',
            help_doc='Please enter a new post name',
            hint='new post name',
            essential=True,
            prevalue=compiled_re.search(selected_post_name).group(2) if compile_flag else selected_post_name
        )
    )
    
    #파일 열어서 title 태그 변경하기
    post_path = f'./_posts/{category_name}/{selected_post_name}/{selected_post_name}.md'
    f = open(post_path, 'r', encoding='utf-8')
    f_raw = f.read()
    f.close()
    
    f_raw = f_raw.replace(f'title: {selected_post_name}', f'title: {new_post_name}', 1)
    
    #기존 파일 제거
    os.remove(post_path)
    
    #포스트 폴더 이름 변경하기
    if compile_flag: new_post_name = f'{compiled_re.search(selected_post_name).group(1)}-{new_post_name}'
    
    new_post_dir = f'./_posts/{category_name}/{new_post_name}/'
    os.renames('/'.join(post_path.split('/')[:-1]), new_post_dir)
    
    #파일 쓰기
    f = open(new_post_dir + new_post_name + '.md', 'w', encoding='utf-8')
    f.write(f_raw)
    f.close()
    
    app.alert(f'Post name {selected_post_name} has been changed to {new_post_name}.')    


async def delete_post(process:CustomProcess, app:TUIApp):
    
    category_scene = ManageCategory.get_category_select_scene('Delete Post')
    
    if category_scene == None: 
        app.alert('You have not created any categories yet.', 'Error')
        return
    
    #카테고리 이름 가져오기
    _, category_name = await process.request_select(category_scene)
    
    #카테고리 내부 포스트 목록 씬 가져오기
    post_list_scene = get_post_list_scene(category_name, prompt='Delete Post', multi_select=True)
    
    if post_list_scene == None:
        app.alert(f"You haven't created any posts yet in this category:{category_name}")
        return
    
    #선택한 포스트 이름 가져오기
    selected_post_name_dict = await process.request_select(post_list_scene)
    
    app.print('[* Delete Post ]')

    #모든 포스트 순회
    app.open_logger(lock=False)
    app.show_loading()
    loading_i, loading_total = 0, len(selected_post_name_dict)
    for post_name in selected_post_name_dict.values():
        app.set_loading_ratio(loading_i / loading_total, msg=f'removing {post_name}')
        loading_i += 1
        await asyncio.sleep(0.001)
        
        post_dir = f'./_posts/{category_name}/{post_name}/'
        
        #포스트 삭제
        app.print(f' Removing {post_dir}')
        shutil.rmtree(post_dir)
    app.hide_loading()
    app.print(f'[* Remove Post Done]')
    app.alert(f'Successfully removed {loading_total} items in category {category_name}.')
    app.close_logger()
            

async def move_post(process:CustomProcess, app:TUIApp):
    category_scene = ManageCategory.get_category_select_scene(prompt='Move Post', include_uncategorized=True)
    
    if category_scene == None: 
        app.alert('You have not created any categories yet.', 'Error')
        return
    
    #카테고리 이름 가져오기
    _, category_name = await process.request_select(category_scene)
    
    #포스트 목록 씬 가져오기
    post_list_scene = get_post_list_scene(category_name, prompt='Move Post', multi_select=True)
    
    if post_list_scene == None:
        app.alert(f"You haven't created any posts yet in this category:{category_name}")
        return
    
    #선택한 포스트 목록 가져오기
    selected_post_name_dict = await process.request_select(post_list_scene)

    #씬 프롬프트 변경
    dest_category_scene = ManageCategory.get_category_select_scene(prompt='Destination')

    #목적지 카테고리 이름 가져오기
    _, dest_category_name = await process.request_select(dest_category_scene)

    app.print('[* Move Post ]')

    #모든 포스트 순회
    app.open_logger(lock=False)
    app.show_loading()
    loading_i, loading_total = 0, len(selected_post_name_dict)
    for post_name in selected_post_name_dict.values():
        app.set_loading_ratio(loading_i / loading_total, msg=f'removing {post_name}')
        loading_i += 1
        await asyncio.sleep(0.001)
        
        post_dir = f'./_posts/{category_name}/{post_name}/'
        new_post_dir = f'./_posts/{dest_category_name}/{post_name}'
        
        #포스트 열어서 categories 태그 수정하기
        post_path = post_dir + post_name + '.md'
        f = open(post_path, 'r', encoding='utf-8')
        f_raw = f.read()
        f.close()
        
        f_raw = f_raw.replace(f'categories: [{category_name}]', f'categories: [{dest_category_name}]', 1)
        
        #파일 쓰기
        f = open(post_path, 'w', encoding='utf-8')
        f.write(f_raw)
        f.close()
        
        #포스트 폴더 이동
        shutil.move(post_dir, new_post_dir)
        app.print(f'  Moving {post_dir}')
        app.print(f'    to {new_post_dir}')
        
    app.hide_loading()
    app.print(f'[* Move Post Done]')
    app.alert(f'Successfully Moved {loading_total} items to category {dest_category_name}.')
    app.close_logger()

async def timestamp_post(process:CustomProcess, app:TUIApp):
    category_scene = ManageCategory.get_category_select_scene('Timestamp Post')
    
    if category_scene == None: 
        app.alert('You have not created any categories yet.', 'Error')
        return
    
    #카테고리 이름 가져오기
    _, category_name = await process.request_select(category_scene)
    
    #카테고리 내부 포스트 목록 씬 가져오기
    post_list_scene = get_post_list_scene(category_name, prompt='Timestamp Post', compiled=True, multi_select=True)
    
    if post_list_scene == None:
        app.alert(f"You haven't created any posts yet in this category:{category_name}")
        return
    
    #선택한 포스트 이름 가져오기
    selected_post_dict = await process.request_select(post_list_scene)

    app.print(f'[* Timestamp Post]')

    #모든 포스트 순회
    app.open_logger(lock=False)
    app.show_loading()
    loading_i, loading_total = 0, len(selected_post_dict)
    for post_name in selected_post_dict.values():
        app.set_loading_ratio(loading_i / loading_total, msg=f'changing {post_name}')
        loading_i += 1
        await asyncio.sleep(0.001)
        
         #포스팅 경로 만들기
        path = f'./_posts/{category_name}/{post_name}'
        
        #타임스탬프 찍기
        new_file_name = timestamp(path)
        app.print(f'  Changed the timestamp of Post {post_name} to {new_file_name}.')
        
    app.hide_loading()
    app.print(f'[* Timestamp Post Done]')
    app.alert(f'Time stamping of total {loading_total} posts has been completed.')
    app.close_logger()


def timestamp(target_post_dir):
    '''receive path like ./_posts/category_name/post_name <- no include .md
    '''
    
    #현재 타임스탬프 만들기
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    splited = target_post_dir.split('/')
    
    pre_path = '/'.join(splited[:-1]) + '/'
    
    #파일이름 추출
    file_name = splited[-1]
    print('filename:', file_name)
    
    old_post_path = f'{target_post_dir}/{file_name}.md'
    
    #타임스탬프 변경
    new_file_name = re.sub(r'\d{4}-\d{2}-\d{2}-(.*)', f'{timestamp}-\\1', file_name)
    
    #파일 이름 변경
    new_post_dir = pre_path + new_file_name
    

    #포스트 폴더 이름 바꾸며 변경
    shutil.move(target_post_dir, new_post_dir)
    
    #옮긴 폴더에서 포스팅파일 이름 바꾸기
    old_post_path = f'{new_post_dir}/{file_name}.md'
    new_post_path = f'{new_post_dir}/{new_file_name}.md'
    
    os.rename(old_post_path, new_post_path)
    
    return new_file_name


def get_post_list_scene(category_name, compiled=False, uncompiled=False, prompt='Empty prompt', multi_select=False):
    compile_re = re.compile(r'\d{4}-\d{2}-\d{2}-.*')
    
    #get post name list of given category name
    category_path = f'./_posts/{category_name}/'
    os.makedirs(category_path, exist_ok=True)

    post_list = os.listdir(category_path)

    if compiled:
        post_list = [post for post in post_list if bool(compile_re.match(post))]
    elif uncompiled:
        post_list = [post for post in post_list if not bool(compile_re.match(post))]
    
    if len(post_list) == 0: return None
    
    scene = Scene(
        main_prompt=f'{prompt} - Select Post',
        items=post_list,
        multi_select=multi_select
    )
    
    return scene
