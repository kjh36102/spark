import ftplib
import os

#ftp_info.yml 있는지 확인하기
info_found_state = os.path.isfile('spark/ftp_info.yml')

#ftp_info.yml 없으면 사용자로부터 로그인 정보 수집
if info_found_state == False:
    print("[! Please input your web FTP info. Don't worry. It will not shown to public.]")
    hostname = input('hostname : ')
    username = input('username : ')
    password = input('password : ')
    basepath = input('basepath (ex=/HDD1/embed): ')
    port = input('port (default=21) : ')
    encoding = input('encoding (default=utf-8) : ')

    if basepath == '': basepath = '/'
    if port == '': port = '21'
    if encoding == '': encoding = 'utf-8'

    #파일로 저장할지 물어보기
    print('[? Do you want to save this in ftp_info.yml? It will not pushed to repository.]')
    print('  (Only recommend on your PC)')
    save_flag = input('save? (y/n) >> ')

    #대답이 y면 저장하기
    if save_flag == 'y':
        f_ftp_info = open('spark/ftp_info.yml', 'w')

        f_ftp_info.write('hostname: ' + hostname + '\n')
        f_ftp_info.write('username: ' + username + '\n')
        f_ftp_info.write('password: ' + password + '\n')

        f_ftp_info.write('basepath: ' + basepath + '\n')
        f_ftp_info.write('port: ' + port + '\n')
        f_ftp_info.write('encoding: ' + encoding + '\n')

        f_ftp_info.close()

        print('[! Your FTP info successfully saved into ftp_info.yml.]')

#ftp_info.yml 이 존재하면 정보 불러오기
print('[! Loading FTP info from ftp_info.yml...]')
f_ftp_info = open('spark/ftp_info.yml', 'r')
while True:
    line = f_ftp_info.readline()
    if not line: break

    raw_line = line[:-1]

    if 'hostname:' in raw_line: hostname = raw_line.split(' ') [1]
    if 'username:' in raw_line: username = raw_line.split(' ') [1]
    if 'password:' in raw_line: password = raw_line.split(' ') [1]
    if 'basepath:' in raw_line: basepath = raw_line.split(' ') [1]
    if 'port:' in raw_line: port = raw_line.split(' ') [1]
    if 'encoding:' in raw_line: encoding = raw_line.split(' ') [1]

f_ftp_info.close()
print('\t...Done')


#cwd 할때 마다 카운트를 센 뒤 나중에 그만큼 상위폴더로 이동하기 위한 변수
cwd_cnt = 0

#폴더 생성 함수, 존재하면 스킵함
def mkdir(ftp, target_dir_path, change_dir=False):
    global cwd_cnt

    dir_list = target_dir_path.split('/')[0:-1]

    for dir_name in dir_list:
        try:
            ftp.mkd(dir_name)
        except ftplib.error_perm as e:
            if e.args[0][:3] == '550':
                pass
            else:
                print('ftplib.error_perm: ', e)
        except UnicodeDecodeError as e:
            pass

        ftp.cwd(dir_name)
        cwd_cnt += 1

    if change_dir == False:
        for i in range(len(dir_list)): ftp.cwd('../')

#파일 업로드
def upload(src_path_list, target_path_list):
    global cwd_cnt

    print('[! Uploading images to FTP Server.]')

    try:
        #두 리스트 크기가 같은지 확인
        if len(src_path_list) != len(target_path_list): raise Exception('Len of src_path_list and target_path_list are not same.')

        with ftplib.FTP() as ftp:
            ftp.connect(host=hostname, port=int(port))
            ftp.encoding = encoding
            ftp.login(user=username, passwd=password)

            ftp.cwd(basepath)

            for src, target in zip(src_path_list, target_path_list):
                print('Src path: ' + src)
                print('Target path: ' + target)

                #디렉토리 생성
                mkdir(ftp, target, change_dir=True)
                
                list = os.listdir(src)

                for file in list:
                    if '.md' in file: continue

                    print('\tUploading ' + file + '...', end='')
                    with open(src + file, 'rb') as f:
                        ftp.storbinary(f'STOR {file}', f)
                        print('\t\tDone')
                    
                for i in range(cwd_cnt): #TODO cwd 명령 리팩토링, 제일앞에 / 를 붙여주면 바로이동 가능
                    ftp.cwd('../')
                cwd_cnt = 0

            ftp.quit()

            print('[! Successfully uploaded images.]')
    except Exception as e:
        print('Error while uploading: ' + e)
    finally:
        ftp.close()

#TODO FTP 서버 내 파일 및 폴더 삭제하는 함수 만들기
def remove(target_path):
    #포스트및 포스트 폴더 삭제
    pass

#TODO _post 폴더 내 파일과 FTP서버 내 파일 동기화하는 함수 만들기
def synchronize(src_path, target_path):
    pass


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

upload(src_list, target_list)
