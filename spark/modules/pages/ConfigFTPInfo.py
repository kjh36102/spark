import sys
sys.path.append('./spark/modules/')
sys.path.append('./spark/modules/pages/')

from TUI import *
from TUI_DAO import *
from TUI_Widgets import CheckableListItem

import os

class ConfigFTPInfoProcess(CustomProcess):
    def __init__(self, app: 'TUIApp') -> None:
        super().__init__(app)
        
        self.funcs = [
            self.see_config_info,
            self.reconfigure,
        ]
        
        func_names = get_func_names(self.funcs)
        
        self.scene = Scene(
            items=func_names
        )
        
    async def main(self):
        idx, val = await self.request_select(self.scene)
        await self.funcs[idx]()
    
    async def see_config_info(self):
        await see_config_info(self, self.app)
    
    async def reconfigure(self):
        await reconfigure(self, self.app)
        
#---------------------------------------------------------------------

async def see_config_info(process:CustomProcess, app:TUIApp):
    
    infos = load_ftp_info()

    app.print_log('in see config info')

    info_str = f"""\
HOSTNAME: {infos['hostname']}, USERNAME: {infos['username']}, PASSWORD: {infos['password']}
IMGBASEURL: {infos['imgbaseurl']}
BASEPATH: {infos['basepath']}, PORT: {infos['port']}, ENCODING: {infos['encoding']}\
"""
    app.alert(info_str)

async def reconfigure(process:CustomProcess, app:TUIApp):
    
    #load prevalue ftp info
    prev_infos = load_ftp_info()
    
    host_name = await process.request_input(
        InputRequest(
            prompt='Hostname.',
            help_doc="Please enter an FTP hostname. ex) 192.168.xxx.xxx, ex) my-domain.com, Don't worry. This is not open to the public. ",
            hint='domain or IP address',
            essential=True,
            prevalue=prev_infos['hostname']
        )
    )
    
    user_name = await process.request_input(
        InputRequest(
            prompt='Username',
            help_doc='Please enter FTP username.',
            hint='username or ID',
            essential=True,
            prevalue=prev_infos['username']
        )
    )
    
    password = await process.request_input(
        InputRequest(
            prompt='Password',
            help_doc="Please enter FTP password",
            hint='password',
            essential=True,
            password=True,
            prevalue=prev_infos['password']
        )
    )
    
    basepath = await process.request_input(
        InputRequest(
            prompt='Basepath',
            help_doc="This is the path to save the local file to the FTP server. ex) /HDD1/embed ",
            hint='path not end with /',
            essential=True,
            prevalue=prev_infos['basepath']
        )
    )

    imgbaseurl = await process.request_input(
        InputRequest(
            prompt='Image base URL',
            help_doc="This is the base URL of URL service provided by your FTP server. ex) http://my-ftp.server.com:8000/list/HDD1/embed/",
            hint='your image server base URL',
            essential=True,
            prevalue=prev_infos['imgbaseurl']
        )
    )
    
    port = await process.request_input(
        InputRequest(
            prompt='Port',
            help_doc="Please enter FTP port. Default: 21",
            hint='port',
            default='21',
            prevalue=prev_infos['port']
        )
    )
    
    encoding = await process.request_input(
        InputRequest(
            prompt='Encoding',
            help_doc="Please enter FTP encoding. Default: utf-8",
            hint='encoding',
            default='utf-8',
            prevalue=prev_infos['encoding']
        )
    )    
    
    f_ftp_info = open('spark/ftp_info.yml', 'w')

    f_ftp_info.write(f'hostname: {host_name}\n')
    f_ftp_info.write(f'username: {user_name}\n')
    f_ftp_info.write(f'password: {password}\n')
    f_ftp_info.write(f'basepath: {basepath}\n')
    f_ftp_info.write(f'imgbaseurl: {imgbaseurl}\n')
    f_ftp_info.write(f'port: {port}\n')
    f_ftp_info.write(f'encoding: {encoding}\n')

    f_ftp_info.close()

    app.alert(f'Your FTP information has been saved in ftp_info.yml.')
    
    
def load_ftp_info():
    file_path = './spark/ftp_info.yml'

    empty_ret = {
            'hostname': '',
            'username': '',
            'password': '',
            'basepath': '',
            'imgbaseurl': '',
            'port': '',
            'encoding': '',
        }

    #return empty string if file not exist
    if not os.path.isfile(file_path):
        return 
    else:
        f = open(file_path, 'r', encoding='utf-8')
        raw_info = f.read()
        f.close()

        lines = raw_info.split('\n')

        ret = {line.split(':')[0] : ':'.join(line.split(':')[1:]).strip() for line in lines if line != ''}

        if len(ret) != len(empty_ret): return empty_ret
        else: return ret