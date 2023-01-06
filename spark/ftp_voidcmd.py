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

print('\t...Done')


#연결
ftp = ftplib.FTP()

ftp.connect(host=hostname, port=int(port))
ftp.encoding = encoding
ftp.login(user=username, passwd=password)

ftp.cwd(basepath)

file_infos = []

while True:
    cmd = input('>> ')
    if cmd == 'quit': break
    elif cmd == 'nlst': print(ftp.nlst())
    elif cmd == 'dir': ftp.dir()
    elif cmd == 'list': 
        ftp.retrlines(cmd, file_infos.append)
        print('file_infos:', file_infos)
    else: print(f'  res: {ftp.voidcmd(cmd)}')

ftp.dir()

try: ftp.quits()
except: ftp.close()