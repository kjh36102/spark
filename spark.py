import sys
sys.path.append('./spark/')

from Selector import Selector

def main_menu():
    idx, _ = Selector(prompt='Welcom to Spark!', item_list=[
        'create new post',
        'synchronize post with FTP server',
        'config post',
        'config category',
        'convert image URL',
        'revert image URL',
        'config FTP info',
        'config CSS style',
        'initialize blog',
    ]).run()

    return idx

def create_new_post():
    print('create_new_post')
    pass

def synchronize_post():
    print('synchronize_post')
    pass

def config_post():
    print('config_post')
    pass

def config_category():
    print('config_category')
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


