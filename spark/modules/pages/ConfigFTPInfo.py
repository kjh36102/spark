import sys
sys.path.append('./spark/modules/')
sys.path.append('./spark/modules/pages/')

from TUI import Scene, Selector, get_func_names

def get_scene():
    funcs = [
        see_config_info,
        reconfigure
    ]

    contents = get_func_names(funcs)

    scene = Scene(
        contents=contents,
        callbacks=funcs, 
    )

    return scene

def see_config_info(spark:Selector):
    f = open('./spark/ftp_info.yml', 'r', encoding='utf-8')
    raw_info = f.read()
    f.close()

    spark.app.alert(raw_info)
    pass

def reconfigure(spark:Selector):
    # spark.prompt_label.text = "Please input your web FTP info. Don't worry. It will not shown to public."

    def _reconfigure_ftp_info(spark:Selector):
        hostname, username, password, basepath, port, encoding = spark.get_input(6)

        if port     == '': port = '21'
        if encoding == '': encoding = 'utf-8'

        f_ftp_info = open('spark/ftp_info.yml', 'w')

        f_ftp_info.write(f'hostname: {hostname}\n')
        f_ftp_info.write(f'username: {username}\n')
        f_ftp_info.write(f'password: {password}\n')
        f_ftp_info.write(f'basepath: {basepath}\n')
        f_ftp_info.write(f'port: {port}\n')
        f_ftp_info.write(f'encoding: {encoding}\n')

        f_ftp_info.close()

        spark.app.alert(f'Your FTP info is saved into ftp_info.yml.')

    spark.request_input(prompt=[
        ('Type FTP server hostname.', 'ex) 192.168.xxx.xxx, ex) my-domain.com'),
        ('Type FTP server username.', 'username or ID'),
        ('Type FTP server password.', 'password'),
        ('Type FTP server basepath', 'root path which synchronize with local ex) /HDD1/embed'),
        ('Type FTP server port.', 'default: 21'),
        ('Type FTP server encoding.', 'default: utf-8'),
    ], callback=_reconfigure_ftp_info)