import ftplib
import os

class FTP:
    def __init__(self) -> None:
        self.session = ftplib.FTP()
        self.hostname = None
        self.username = None
        self.password = None
        self.basepath = '/'
        self.port = 21
        self.encoding = 'utf-8'
    
    def connect(self):
        err_flag = True

        try:
            print(f'[* Waiting response from {self.hostname}...]')
            print('\tif this takes so long, check out hostname and port.')
            self.session.connect(host=self.hostname, port=int(self.port))
            print(f'[* Connected to {self.hostname}]')
            self.session.encoding = self.encoding
            self.session.login(user=self.username, passwd=self.password)

            self.session.cwd(self.basepath)
            err_flag = False
        except TimeoutError:
            print('[! Failed to connect. You should check out your hostname and port in ftp_info.yml.]')
        except ftplib.error_perm as e:
            if e.args[0][:3] == '530': print('[! Failed to login. Check out your username and password.]')
        
        if err_flag: exit(1)

    def close(self):
        try: self.session.quit()
        except Exception as e:
            print('Failed to close FTP: ', e)
            self.session.close()

    def load_info(self):
        #ftp_info.yml 있는지 확인하기
        info_found_state = os.path.isfile('spark/ftp_info.yml')

        if info_found_state:
            #파일 읽어서 변수 초기화
            print('[* Loading FTP info from ftp_info.yml...]')

            f_ftp_info = open('spark/ftp_info.yml', 'r')

            while True:
                line = f_ftp_info.readline()
                if not line: break

                raw_line = line[:-1]

                if 'hostname:'  in raw_line: self.hostname = raw_line.split(' ') [1]
                if 'username:'  in raw_line: self.username = raw_line.split(' ') [1]
                if 'password:'  in raw_line: self.password = raw_line.split(' ') [1]
                if 'basepath:'  in raw_line: self.basepath = raw_line.split(' ') [1]
                if 'port:'      in raw_line: self.port     = raw_line.split(' ') [1]
                if 'encoding:'  in raw_line: self.encoding = raw_line.split(' ') [1]

            print('\t...Done')
        else: self.configure()

    def configure(self):
        print("[* Please input your web FTP info. Don't worry. It will not shown to public.]")
        hostname = input('hostname : ')
        username = input('username : ')
        password = input('password : ')
        basepath = input('basepath (ex=/HDD1/embed): ')
        port = input('port (default=21) : ')
        encoding = input('encoding (default=utf-8) : ')

        self.hostname = hostname
        self.username = username
        self.password = password
        if basepath != '': self.basepath = basepath
        if port     != '': self.port = port
        if encoding != '': self.encoding = encoding

        f_ftp_info = open('spark/ftp_info.yml', 'w')

        f_ftp_info.write(f'hostname: {self.hostname}\n')
        f_ftp_info.write(f'username: {self.username}\n')
        f_ftp_info.write(f'password: {self.password}\n')
        f_ftp_info.write(f'basepath: {self.basepath}\n')
        f_ftp_info.write(f'port: {self.port}\n')
        f_ftp_info.write(f'encoding: {self.encoding}\n')

        f_ftp_info.close()

        print('[* Your FTP info is saved into ftp_info.yml.]')

    #폴더 생성 함수, 존재하면 스킵함
    def mkdir(self, target_dir_path, change_dir=False):
        dir_list = target_dir_path.split('/')[0:-1]

        for dir_name in dir_list:
            try:
                self.session.mkd(dir_name)
            except ftplib.error_perm as e:
                if e.args[0][:3] == '550': pass
                else: print('ftplib.error_perm: ', e)
        
            try: self.session.cwd(dir_name)
            except ftplib.error_perm:
                print('[! Failed to create directory. Check out your basepath in ftp_info.yml]')
                exit(1)

        if change_dir == False: self.session.cwd(self.basepath)

        #파일 동기화
    def synchronize(self, src_path_list, target_path_list):
        print('[* Synchronize files with FTP Server.]')

        try:
            #두 리스트 크기가 같은지 확인
            if len(src_path_list) != len(target_path_list): raise Exception('Len of src_path_list and target_path_list are not same.')

            for src, target in zip(src_path_list, target_path_list):
                self.session.cwd(self.basepath)

                print('  Src path:\t' + src)
                print('  Target path:\t' + target, end='\n\n')

                #디렉토리 생성
                self.mkdir(target, change_dir=True)
                
                #remote_file_sizes 구하기
                remote_file_infos = []  #4번 파일 사이즈, 8번 파일 이름
                self.session.retrlines('LIST', remote_file_infos.append)

                remote_file_sizes = {}  
                for raw_str in remote_file_infos:   #remote_file_infos 정제
                    file_name = raw_str.split(':')[1][3:]
                    file_size = ' '.join(raw_str.split()).split()[4]

                    remote_file_sizes[file_name] = file_size

                # print('remote_file_sizes:', remote_file_sizes)

                #local_file_sizes 구하기
                local_file_names = os.listdir(src)
                local_file_sizes = {}
                
                for file in local_file_names:
                    local_file_sizes[file] = os.path.getsize(src + file)

                # print('local_file_sizes:', local_file_sizes)

                #집합으로 변환
                local_name_set = set(local_file_names)
                remote_name_set = set(remote_file_sizes.keys())
                
                # print('local_name_set:', local_name_set)
                # print('remote_name_set:', remote_name_set)

                append_list = local_name_set - remote_name_set
                remove_list = remote_name_set - local_name_set
                intersect_list = local_name_set.intersection(remote_name_set)

                # print('append_list:', append_list)
                # print('remove_list:', remove_list)
                # print('intersect_list:', intersect_list)

                sync_cnt = 0

                for file in append_list:
                    # if '.md' in file: continue

                    print('\t+ Uploading\t' + file)
                    self.session.storbinary(f'STOR {file}', open(src + file, 'rb'))
                    sync_cnt += 1

                for file in intersect_list:
                    # print(f'file name: {file}, local_size: {local_file_sizes[file]}, remote_size: {remote_file_sizes[file]}')

                    if int(local_file_sizes[file]) != int(remote_file_sizes[file]):
                        print('\t* Updating\t' + file)
                        self.session.storbinary(f'STOR {file}', open(src + file, 'rb')) 
                        sync_cnt += 1
                
                for file in remove_list:
                    print('\t- Removing\t' + file)
                    self.session.delete(file)  
                    sync_cnt += 1

                if sync_cnt == 0: print('\tNothing to synchronize. Already up to date.')
                print()

            self.session.cwd(self.basepath)
            print('[* Successfully synchronized.]')
        except Exception as e:
            print('Error while uploading: ' + e)

    def convert_path(src):
        src = src.replace('\\', '/')
        src += '/'
    
        target = src.split('_posts/')[1]
        src = '_posts/' + target

        return src, target

if __name__ == '__main__':
    ftp = FTP()
    ftp.load_info()
    ftp.connect()

    src_list = []
    target_list = []

    while True:
        input_str = input('input file dir >> ')

        if input_str == 'x': break

        src, target = FTP.convert_path(input_str)

        src_list.append(src)
        target_list.append(target)

        print(src_list, target_list)

    ftp.synchronize(src_list, target_list)

    ftp.close()
