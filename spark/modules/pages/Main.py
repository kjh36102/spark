import sys
sys.path.append('./spark/modules/')
sys.path.append('./spark/modules/pages/')

from TUI import TUIApp
from TUI_DAO import Scene, get_func_names, InputRequest
from TUI_Widgets import CheckableListItem
from TUI_events import CustomProcess

from pages import ManageCategory
from pages import ManagePost

def get_scene():

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
            initialize_blog,
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

    func_names = get_func_names(funcs)

    scene = Scene(
        main_prompt='Welcome to Spark!',
        items=[CheckableListItem(func_name) for func_name in func_names],
        help_title='Index description',
        help_doc=help
    )

    return scene

#manage post 카테고리에서 불러오는 방식으로 바꾸기
def create_new_post(app:TUIApp, item:CheckableListItem):
    ManagePost.create_post(app, item)

def synchronize_post(spark):
    pass

def commit_and_push(spark):
    pass

def manage_post(app:TUIApp, _):
    app.push_scene(ManagePost.get_scene())

def manage_category(app:TUIApp, _):
    app.push_scene(ManageCategory.get_scene())

def convert_image_url(spark):
    pass

def revert_image_url(spark):
    pass

def config_ftp_info(spark:TUIApp):
    pass

def change_css_theme(spark):
    pass

def initialize_blog(spark):
    pass