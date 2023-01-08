import sys
sys.path.append('./spark/modules/')

from Selector import Selector

def main():
    funcs = [
        create_new_post,
        synchronize_post,
        commit_and_push,
        manage_post,
        manage_category,
        convert_image_url,
        revert_image_url,
        config_ftp_info,
        change_css_theme,
        initialize_blog
    ]

    help ='''\
create new post - Create new post automatically.
synchronize post - Synchronize post with FTP server.
commit & push - commit and push to github.
manage post - Managing settings about specific post.
manage category - Managing your categories.
convert image URL - Change local image URL to embeded URL from FTP server.
revert image URL -  Change embeded URL to local image URL.
config FTP info - Config FTP info for using synchronize feature.
change CSS theme - Change blog css theme.
initialize blog - After clone from github, must run this once.\
'''

    #make func names list
    func_names = [func.__name__.replace('_', ' ') for func in funcs]

    idx, _ = Selector(prompt='Welcom to Spark!', item_list=func_names, help_text=help).run()

    funcs[idx]()


def create_new_post():
    print('create_new_post')
    pass

def synchronize_post():
    print('synchronize_post')
    pass

def commit_and_push():
    print('commit and push')
    pass

def manage_post():
    print('manage_post')
    pass

def manage_category():
    print('manage_category')

    def create_category():
        print('create_category')

        new_name = input('Input name of new Category >> ')
        print(new_name)
        pass

    def rename_category():
        print('rename_category')
        pass

    def delete_category():
        print('delete_category')
        pass

    funcs = [
        create_category,
        rename_category,
        delete_category
    ]

    func_names = [func.__name__.replace('_', ' ') for func in funcs]

    idx, _ = Selector(prompt='manage category', item_list=func_names).run()

    funcs[idx]()

def convert_image_url():
    print('convert_image_url')
    pass

def revert_image_url():
    print('revert_image_url')
    pass

def config_ftp_info():
    print('config_ftp_info')
    pass

def change_css_theme():
    print('config_css_style')
    pass

def initialize_blog():
    print('initialize blog')
    pass


if __name__ == '__main__':
    try: main()
    except Exception as e:
        print('!Error:', e)