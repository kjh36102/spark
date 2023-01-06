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
        self.cwd_level = 0
    
    def connect(self):
        self.session.connect(host=self.hostname, port=int(self.port))
        self.session.encoding = self.encoding
        self.session.login(user=self.username, passwd=self.password)

        self.session.cwd(self.basepath)

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
            print('[! Loading FTP info from ftp_info.yml...]')

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
        print("[! Please input your web FTP info. Don't worry. It will not shown to public.]")
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
        f_ftp_info.write(f'port:     {self.port}\n')
        f_ftp_info.write(f'encoding: {self.encoding}\n')

        f_ftp_info.close()

        print('[! Your FTP info is saved into ftp_info.yml.]')

    def go_basepath(self):
        while self.cwd_level > 0: self.cwd('../')
    
    def cwd(self, dirname):
        code = self.session.voidcmd('CWD ' + dirname)[:3]

        if code != '250': return

        if dirname == '../': 
            if self.cwd_level <= 0: 
                self.session.voidcmd('CWD ' + self.basepath)
                self.cwd_level = 0
                return

            self.cwd_level -= 1
        else:
            self.cwd_level += 1

    #폴더 생성 함수, 존재하면 스킵함
    def mkdir(self, target_dir_path, change_dir=False):
        dir_list = target_dir_path.split('/')[0:-1]

        for dir_name in dir_list:
            try:
                self.session.mkd(dir_name)
            except ftplib.error_perm as e:
                if e.args[0][:3] == '550':
                    pass
                else:
                    print('ftplib.error_perm: ', e)
            except UnicodeDecodeError as e:
                pass

            self.session.cwd(dir_name)

        if change_dir == False: self.session.cwd(self.basepath)

        #파일 업로드
    def upload(self, src_path_list, target_path_list):
        print('[! Uploading images to FTP Server.]')

        try:
            #두 리스트 크기가 같은지 확인
            if len(src_path_list) != len(target_path_list): raise Exception('Len of src_path_list and target_path_list are not same.')

            for src, target in zip(src_path_list, target_path_list):
                self.session.cwd(self.basepath)

                print('Src path: ' + src)
                print('Target path: ' + target)

                #디렉토리 생성
                self.mkdir(target, change_dir=True)
                
                list = os.listdir(src)

                for file in list:
                    if '.md' in file: continue

                    print('\tUploading ' + file + '...', end='')
                    with open(src + file, 'rb') as f:
                        self.session.storbinary(f'STOR {file}', f)
                        print('\t\tDone')

            self.session.cwd(self.basepath)
            print('[! Successfully uploaded images.]')
        except Exception as e:
            print('Error while uploading: ' + e)


ftp = FTP()
ftp.load_info()
ftp.connect()

src_list = []
target_list = []

while True:
    src = input('input file dir >> ')

    if src == 'x': break

    src = src.replace('\\', '/')
    src += '/'

    target = src[7:]

    src_list.append(src)
    target_list.append(target)

ftp.upload(src_list, target_list)

ftp.close()
