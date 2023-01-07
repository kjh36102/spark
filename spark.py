import sys
sys.path.append('./spark/modules/')

from Selector import Selector

def main_menu():
    menu = [
        'create new post',
        'synchronize post',
        'manage post',
        'manage category',
        'convert image URL',
        'revert image URL',
        'config FTP info',
        'config CSS style',
        'initialize blog',
    ]

    help ='''\
create new post - Create new post automatically.
synchronize post - Synchronize post with FTP server.
manage post - Managing settings about specific post.
manage category - Managing your categories.
convert image URL - Change local image URL to embeded URL from FTP server.
revert image URL -  Change embeded URL to local image URL.
config FTP info - Config FTP info for using synchronize feature.
change CSS theme - Change blog css theme.
initialize blog - After clone from github, must run this once.
'''

    idx, _ = Selector(prompt='Welcom to Spark!', item_list=menu, help_text=help).run()

    return idx

def create_new_post():
    print('create_new_post')
    pass

def synchronize_post():
    print('synchronize_post')
    pass

def config_post():
    print('manage_post')
    pass

def config_category():
    print('manage_category')
    pass

def convert_image_url():
    print('convert_image_url')
    pass

def revert_image_url():
    print('revert_image_url')
    pass

def config_ftp_info():
    print('config_ftp_info')
    pass

def config_css_style():
    print('config_css_style')
    pass

def initialize_blog():
    print('initialize blog')
    pass

# main -------------------------------------------
try:
    idx = main_menu() + 1

    if idx == 1: create_new_post()
    elif idx == 2: synchronize_post()
    elif idx == 3: config_post()
    elif idx == 4: config_category()
    elif idx == 5: convert_image_url()
    elif idx == 6: revert_image_url()
    elif idx == 7: config_ftp_info()
    elif idx == 8: config_css_style()
    elif idx == 9: initialize_blog()
    else: raise IndexError('Out of selection range')

except Exception as e:
    print('!Error:', e)


