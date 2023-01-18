import sys
sys.path.append('./spark/modules/')
sys.path.append('./spark/modules/pages/')

from pages import ConfigGitCommand
from pages import ConfigFTPInfo

from TUI import *
from TUI_DAO import *
from TUI_Widgets import CheckableListItem

import ManageCategory
import ConfigFTPInfo
import ManagePost

from datetime import datetime
import os
import re
import subprocess

import ftplib
class FtpManager:
    def __init__(self, app:TUIApp) -> None:
        self.app = app
        info_dict = ConfigFTPInfo.load_ftp_info()

        self.session = ftplib.FTP()
        self.hostname = info_dict['hostname']
        self.username = info_dict['username']
        self.password = info_dict['password']
        self.basepath = info_dict['basepath']
        self.port = info_dict['port']
        self.encoding = info_dict['encoding']

    def connect(self):
        err_flag = True

        try:
            self.app.print(f'[* Waiting response from {self.hostname}...]')
            self.app.print('  if this takes so long, check out hostname and port.')
            self.session.connect(host=self.hostname, port=int(self.port))
            self.app.print(f'[* Connected to {self.hostname}]')
            self.session.encoding = self.encoding
            self.session.login(user=self.username, passwd=self.password)

            self.session.cwd(self.basepath)
            err_flag = False
        except TimeoutError:
            self.app.print('[! Failed to connect. You should check out your hostname and port in ftp_info.yml.]')
        except ftplib.error_perm as e:
            if e.args[0][:3] == '530': self.app.print('[! Failed to login. Check out your username and password.]')
        
        if err_flag: exit(1)

    def close(self):
        try: self.session.quit()
        except Exception as e:
            self.app.print('Failed to close FTP: ', e)
            self.session.close()

    #폴더 생성 함수, 존재하면 스킵함
    def mkdir(self, target_dir_path, change_dir=False):
        dir_list = target_dir_path.split('/')[0:-1]

        for dir_name in dir_list:
            try:
                self.session.mkd(dir_name)
            except ftplib.error_perm as e:
                if e.args[0][:3] == '550': pass
                else: self.app.print('ftplib.error_perm: ', e)
        
            try: self.session.cwd(dir_name)
            except ftplib.error_perm:
                self.app.print('[! Failed to create directory. Check out your basepath in ftp_info.yml]')
                exit(1)

        if change_dir == False: self.session.cwd(self.basepath)

    def rmdir(self, target_dir_path):
        """Recursively delete a directory tree on a remote server."""
        wd = self.session.pwd()

        try:
            names = self.session.nlst(target_dir_path)
        except ftplib.all_errors as e:
            # some FTP servers complain when you try and list non-existent paths
            self.app.print(f'    Could not remove {target_dir_path}: {e}')
            return

        for name in names:
            if os.path.split(name)[1] in ('.', '..'): continue

            self.app.print(f'    Removing {name}')

            try:
                self.session.cwd(name)  # if we can cwd to it, it's a folder
                self.session.cwd(wd)  # don't try a nuke a folder we're in
                self.rmdir(name)
            except ftplib.all_errors:
                self.session.delete(name)

        try:
            self.session.rmd(target_dir_path)
        except ftplib.all_errors as e:
            self.app.print(f'    Could not remove {target_dir_path}: {e}')


        #파일 동기화
    async def synchronize(self, src_path_list, target_path_list):
        self.app.print('[* Start synchronizing local files with the FTP server.]')

        try:
            #두 리스트 크기가 같은지 확인
            if len(src_path_list) != len(target_path_list): raise Exception('Len of src_path_list and target_path_list are not same.')

            # self.app.show_loading()
            # work_i, work_total = 0, len(src_path_list)

            actual_work = 0

            self.app.show_loading()
            loading_i, loading_total = 0, len(src_path_list)
            for src, target in zip(src_path_list, target_path_list):
                self.app.set_loading_ratio(loading_i/loading_total, msg=f'working on {target}')
                await asyncio.sleep(0.001)
                #로딩박스 표시
                # work_i += 1
                # self.app.set_loading_ratio(work_i / work_total, f'working on {target}')

                self.session.cwd(self.basepath)

                #디렉토리 생성
                self.mkdir(target, change_dir=True)
                
                #remote_file_sizes 구하기
                remote_file_infos = []  #4번 파일 사이즈, 8번 파일 이름
                self.session.retrlines('LIST', remote_file_infos.append)

                remote_file_sizes = {}  
                for raw_str in remote_file_infos:   #remote_file_infos 정제
                    await asyncio.sleep(0.001)
                    file_name = raw_str.split(':')[1][3:]
                    file_size = ' '.join(raw_str.split()).split()[4]

                    remote_file_sizes[file_name] = file_size

                # self.app.print_log('remote_file_sizes:', remote_file_sizes)


                #local_file_sizes 구하기
                local_file_names = os.listdir(src)
                local_file_sizes = {}
                
                for file in local_file_names:
                    await asyncio.sleep(0.001)
                    local_file_sizes[file] = os.path.getsize(src + file)

                # self.app.print_log('local_file_sizes:', local_file_sizes)

                #집합으로 변환
                local_name_set = set(local_file_names)
                remote_name_set = set(remote_file_sizes.keys())
                
                # self.app.print_log('local_name_set:', local_name_set)
                # self.app.print_log('remote_name_set:', remote_name_set)

                append_list = local_name_set - remote_name_set
                remove_list = remote_name_set - local_name_set
                intersect_list = local_name_set.intersection(remote_name_set)
                update_list = [file for file in intersect_list if int(local_file_sizes[file]) != int(remote_file_sizes[file])]


                need_change_count = (len(append_list) + len(remove_list) + len(update_list))
                actual_work += need_change_count
                # self.app.print_log('need_change_count:', need_change_count)

                if need_change_count > 0:
                    self.app.print(' ')
                    self.app.print('  Src path:  ' + src)
                    self.app.print('  Target path:  ' + target + '\n')

                # self.app.print_log('append_list:', append_list)
                # self.app.print_log('remove_list:', remove_list)
                # self.app.print_log('update_list:', update_list)

                
                for file in append_list:
                    await asyncio.sleep(0.001)
                    # if '.md' in file: continue
                    self.app.print('  + Uploading  ' + file)
                    self.session.storbinary(f'STOR {file}', open(src + file, 'rb'))

                for file in update_list:
                    await asyncio.sleep(0.001)
                    # self.app.print_log(f'file name: {file}, local_size: {local_file_sizes[file]}, remote_size: {remote_file_sizes[file]}')
                    self.app.print('  * Updating  ' + file)
                    self.session.storbinary(f'STOR {file}', open(src + file, 'rb')) 
                
                
                for file in remove_list:
                    await asyncio.sleep(0.001)
                    self.app.print('  - Removing  ' + file)
                    self.session.delete(file) 

                loading_i += 1
                
            # 로딩박스 해제
            self.app.hide_loading()
            
            if actual_work == 0:
                self.app.print(' ')
                self.app.print('  Nothing to synchronize. Already up to date.')
            
            self.session.cwd(self.basepath)
            self.app.print(' ')
            self.app.print('[* Synchronization is complete.]')

            
        except Exception as e:
            self.app.print(f'  Error while uploading file:{src} , e:{e}')

    def convert_path(src):
        # if src
        # src = src.replace('\\', '/')
        src += '/'
    
        target = src.split('_posts/')[1]
        src = '_posts/' + target

        return src, target


class AdvancedMenuProcess(CustomProcess):
    def __init__(self, app: 'TUIApp') -> None:
        super().__init__(app)

        self.funcs = [
            self.Compile_post,
            self.Decompile_post,
            self.Sync_local_with_FTP,
        ]

        func_names = get_func_names(self.funcs)

        self.scene = Scene(
            items=func_names,
            main_prompt='Advanced Menu',
        )

    async def main(self):
        idx, val = await self.request_select(self.scene)
        await self.funcs[idx]()


    async def Compile_post(self): 
        await asyncio.create_task(compile_post(self, self.app))
        # await compile_post(self, self.app)
    async def Decompile_post(self): 
        await asyncio.create_task(decompile_post(self, self.app))
        # await decompile_post(self, self.app)
    async def Sync_local_with_FTP(self):
        await asyncio.create_task(sync_local_with_FTP(self, self.app))
        # await sync_local_with_FTP(self, self.app)

async def compile_post(process:CustomProcess, app:TUIApp):
    #get category scene
    category_scene = ManageCategory.get_category_select_scene(prompt='Compile Post')

    #if there is no category
    if category_scene == None:
        app.alert("You haven't created any categories yet.")
        return

    _, selected_category = await process.request_select(category_scene)

    #get post select scene
    post_scene = ManagePost.get_post_list_scene(selected_category, prompt='Compile Post', uncompiled=True, multi_select=True)

    #포스트가 하나도 없으면 탈출
    if post_scene == None:
        app.alert(f"It seems there is no compilable posts in this category:{selected_category}")
        return

    #비컴파일 포스트 가져오기
    uncompiled_list = await process.request_select(post_scene)
    uncompiled_list = uncompiled_list.items()

    #ftp 정보에서 imgbaseurl 가져오기
    ftp_info = ConfigFTPInfo.load_ftp_info()
    imgbaseurl = ftp_info['imgbaseurl']

    #정규식 객체 컴파일
    compiled_re = re.compile(r'\!\[(.*)\]\(./([^http].*)\)')

    app.print(f'[* Compile Post]')

    app.open_logger(lock=True)
    app.show_loading()
    loading_i, loading_max = 0, len(uncompiled_list)
    for _, post_name in uncompiled_list:
        app.set_loading_ratio(loading_i/loading_max, f'Converting {post_name}...')
        loading_i += 1
        asyncio.sleep(0.001)
        _compile(process, app, selected_category, post_name, compiled_re, imgbaseurl)

    app.hide_loading()
    app.open_logger(lock=False)
    app.print(f'[* Compile Post Done]')
    app.alert(f'Compiling {loading_max} posts in category {selected_category} all done.')

async def decompile_post(process:CustomProcess, app:TUIApp):
        #get category scene
    category_scene = ManageCategory.get_category_select_scene(prompt='Decompile Post')

    #if there is no category
    if category_scene == None:
        app.alert("You haven't created any categories yet.")
        return

    _, selected_category = await process.request_select(category_scene)

    #get post select scene
    post_scene = ManagePost.get_post_list_scene(selected_category, prompt='Decompile Post', compiled=True, multi_select=True)

    #포스트가 하나도 없으면 탈출
    if post_scene == None:
        app.alert(f"It seems there is no decompilable posts in this category:{selected_category}")
        return

    #컴파일 포스트 가져오기
    compiled_list = await process.request_select(post_scene)
    compiled_list = compiled_list.items()

    #정규식 객체 컴파일
    compiled_re = re.compile(r'\!\[(.*)\]\([http].*\/(.*)\)')

    app.open_logger(lock=True)
    app.show_loading()
    loading_i, loading_max = 0, len(compiled_list)

    for _, post_name in compiled_list:
        app.print('---------------------')
        app.set_loading_ratio(loading_i/loading_max, f'Converting {post_name}...')
        loading_i += 1
        await asyncio.sleep(0.001)

        #기존 포스트 경로 가져오기
        app.print(f'    Decompile target post:{post_name}')
        post_dir = f'./_posts/{selected_category}/{post_name}/'
        post_path = post_dir + f'{post_name}.md'

        #파일 이름 앞에 날짜 떼기
        app.print('  Changing file name...')
        new_post_name = '-'.join(post_name.split('-')[3:])

        #기존 파일 읽기
        app.print('  Reading original file content...')
        f = open(post_path, 'r', encoding='utf-8')
        raw_f = f.read()
        f.close()

        #기존 파일에서 이미지 주소 변환
        app.print('  Converting local url to embeded url...')
        raw_f = raw_f.replace(f'title: {post_name}', f'title: {new_post_name}', 1)
        raw_f = compiled_re.sub(f'![\\1](./\\2)', raw_f)

        #기존 포스팅 제거
        app.print('  Removing original post...')
        os.remove(post_path)

        #새로운 포스팅 추가
        app.print('  Writing new post...')
        f = open(post_dir + f'{new_post_name}.md', 'w', encoding='utf-8')
        f.write(raw_f)
        f.close()

        #폴더 이름 변경
        app.print('  Changing post dir name...')
        new_post_dir = f'./_posts/{selected_category}/{new_post_name}/'
        os.renames(post_dir, new_post_dir)

        app.print(f'      Decompile {post_name} is done!')
        
    app.hide_loading()
    app.open_logger(lock=False)
    app.alert(f'Compiling {loading_max} posts in category {selected_category} all done.')

async def sync_local_with_FTP(process:CustomProcess, app:TUIApp):
    #ftp 정보 검사하기
    if ConfigFTPInfo.load_ftp_info()['hostname'] == '':
        app.alert('You must configure FTP server info before you can use this feature.', 'Error')
        return
    
    app.open_logger(lock=True)
    app.print_bar()

    #ftp 연결
    ftp = FtpManager(app)
    ftp.connect()
    
    app.print('Preparing data....')

    local_base_path = './_posts/'

    #리모트 카테고리 리스트 만들기
    remote_categories = ftp.session.nlst()

    #로컬 카테고리 리스트 만들기
    local_categories = os.listdir('./_posts/')

    #집합으로 변환하기
    local_category_set = set(local_categories)
    remote_category_set = set(remote_categories)

    #지워야될 카테고리 구하기
    remote_category_need_delete_set = remote_category_set - local_category_set

    #리모트 카테고리 지우기
    app.print('Removing all non-exist category...')
    for category_need_delete in remote_category_need_delete_set:
        await asyncio.sleep(0.001)
        ftp.rmdir(category_need_delete)
        

    if len(remote_category_need_delete_set) == 0:
        app.print(' No categories to be deleted')

    #카테고리 다시 가져오기
    remote_categories = ftp.session.nlst()
    
    app.print('Removing all non-exist posts from each category...')
    
    for i, category in enumerate(remote_categories):
        await asyncio.sleep(0.001)
        app.print(f'  Searching inside category {category}...')
        
        remote_post_set = set(ftp.session.nlst(category))
        local_post_set = set([f'{category}/{post}' for post in os.listdir('./_posts/'+category)])

        remote_post_need_delete_set = remote_post_set - local_post_set

        app.show_loading()
        loading_i, loading_total = 0, len(remote_post_need_delete_set)
        for post in remote_post_need_delete_set:
            app.set_loading_ratio(loading_i/loading_total, msg=f'removing {post}')
            ftp.rmdir(post)
        app.hide_loading()
        
        if len(remote_post_need_delete_set) == 0:
            app.print('   No posts to be deleted')
    
    src_list = []
    target_list = []
    
    #로컬 카테고리 순회
    app.print('Building update list...')
    for category_name in local_categories:
        await asyncio.sleep(0.001)

        post_list = os.listdir(local_base_path + category_name)

        #카테고리 내부 포스트 이름 순회
        app.show_loading()
        loading_i, loading_total = 0, len(post_list)
        for post_name in post_list:
            await asyncio.sleep(0.001)
            app.set_loading_ratio(loading_i/loading_total, msg=f'working on {post_name}')
            
            post_path = local_base_path + category_name + '/' + post_name + '/'

            target = post_path.split('_posts/')[1]

            src_list.append(post_path)
            target_list.append(target)
        app.hide_loading()

    #업로드
    await asyncio.create_task(ftp.synchronize(src_list, target_list))
    ftp.close()

    app.open_logger(lock=False)
    pass

async def compile_and_push(process:CustomProcess, app:TUIApp):
    #카테고리 멀티 선택 메뉴 보여주기
    category_scene = ManageCategory.get_category_select_scene('Compile And Push', multi_select=True, include_uncategorized=True)
    
    if category_scene == None: 
        app.alert('You have not created any categories yet.', 'Error')
        return
    
    #선택한 카테고리들 가져오기
    category_name_dic = await process.request_select(category_scene)
    category_names = category_name_dic.values()
    
    #깃 정보 검사하기
    git_cmd = ConfigGitCommand.load_git_command()
    
    if git_cmd == '':
        app.alert('You must set the git command before you can use this feature.', 'Error')
        return
    
    #ftp 정보 검사하기
    if ConfigFTPInfo.load_ftp_info()['hostname'] == '':
        app.alert('You must configure FTP server info before you can use this feature.', 'Error')
        return
    
    
    #정규식 객체 컴파일
    compiled_compile_re = re.compile(r'\d{4}-\d{2}-\d{2}-.*')
    compiled_url_re = re.compile(r'\!\[(.*)\]\(./([^http].*)\)')
    
    #ftp 정보에서 imgbaseurl 가져오기
    ftp_info = ConfigFTPInfo.load_ftp_info()
    imgbaseurl = ftp_info['imgbaseurl']
    
    #모든 카테고리 순회
    app.open_logger(lock=False)
    
    app.print(f'[* Compile And Push]')
   
    cnt = 0
   
    for category_name in category_names:
        app.print(f'  Checking inside category {category_name}')
        
        #포스트 이름 가져오기
        category_dir = f'./_posts/{category_name}'
        try:
            post_list = os.listdir(category_dir)
        except FileNotFoundError:
            os.makedirs(category_dir)
        finally: post_list = os.listdir(category_dir)
        
        #디컴파일 된것만 추출하기
        post_list = [post for post in post_list if not bool(compiled_compile_re.match(post))]
        
        if len(post_list) == 0:
            app.print('    Nothing to compile.')
            continue
        
        app.show_loading()
        loading_i, loading_total = 0, len(post_list)
        for post_name in post_list:
            app.set_loading_ratio(loading_i / loading_total, msg=f'removing {post_name}')
            loading_i += 1
            await asyncio.sleep(0.001)
            
            _compile(process, app, category_name, post_name, compiled_url_re, imgbaseurl)
            cnt += 1
        app.hide_loading()    
    
    error_flag = False
    
    #로컬 파일 ftp에 업데이트
    try:
        #깃 커밋 및 푸쉬
        cmd_list = list(map(str.strip, git_cmd.split(';')[:-1]) )
        
        for cmd in cmd_list:
            res = subprocess.getstatusoutput(cmd)[1]
            buf = res.split('\n')
            
            for line in buf:
                await asyncio.sleep(0.001)
                app.print(line)
    except Exception as e:
        app.print(f'Error occured while trying to git push: {e}')  
        error_flag = True
        
        
    try:
        sync_local_with_FTP(process, app)
        pass
    except Exception as e:
        app.print(f'Error occured while trying to synchronize with FTP server: {e}') 
        error_flag = True
        
    
    app.print(f'[* Compile And Push Done]')
    if error_flag:
        app.alert(f'Successfully compiled {cnt} posts but there was an unknown error. Check out git command and ftp info.')
    else:
        app.alert(f'Successfully compiled and pushed {cnt} posts in whole category.')
    app.close_logger()
    
    
    
    pass

def _compile(process:CustomProcess, app:TUIApp, category_name, post_name, regex_instance, imgbaseurl):
    app.print('---------------------')
    
    #기존 포스트 경로 가져오기
    post_dir = f'./_posts/{category_name}/{post_name}/'
    post_path = post_dir + f'{post_name}.md'
    
    app.print(f'    Compiling target post: {post_dir}')

    #파일 이름 앞에 날짜 붙이기
    # app.print('  Changing file name...')
    date_str = datetime.now().strftime('%Y-%m-%d')
    new_post_name = f'{date_str}-{post_name}'

    #기존 파일 읽기
    # app.print('  Reading original file content...')
    f = open(post_path, 'r', encoding='utf-8')
    raw_f = f.read()
    f.close()

    #기존 파일에서 이미지 주소 변환
    app.print('      Converting local url to embeded url...')
    post_name_without_space = new_post_name.replace(' ', '%20')
    raw_f = regex_instance.sub(f'![\\1]({imgbaseurl}{category_name}/{post_name_without_space}/\\2)', raw_f)

    #기존 포스팅 제거
    app.print('      Removing original post...')
    os.remove(post_path)

    #새로운 포스팅 추가
    app.print('      Writing new post...')
    f = open(post_dir + f'{new_post_name}.md', 'w', encoding='utf-8')
    f.write(raw_f)
    f.close()

    #폴더 이름 변경
    app.print('      Changing post dir name...')
    new_post_dir = f'./_posts/{category_name}/{new_post_name}/'
    os.renames(post_dir, new_post_dir)

    app.print(f'        Compile {post_name} is done!')