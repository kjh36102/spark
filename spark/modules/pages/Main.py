import sys
sys.path.append('./spark/modules/')

from TUI import Scene

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

    func_names = [func.__name__ for func in funcs]

    scene = Scene(
        contents=func_names,
        callbacks=funcs,
        callbacks_args=[()for _ in range(len(funcs))],
        help_doc=help,
    )

    return scene

def create_new_post(spark):
    spark.prompt_label.text = ('create_new_post')
    pass

def synchronize_post(spark):
    spark.prompt_label.text = ('synchronize_post')
    pass

def commit_and_push(spark):
    spark.prompt_label.text = ('commit and push')
    pass

def manage_post(spark):
    spark.prompt_label.text = ('manage_post')
    pass

def manage_category(spark):
    spark.prompt_label.text = ('manage_category')
    pass

def convert_image_url(spark):
    spark.prompt_label.text = ('convert_image_url')
    pass

def revert_image_url(spark):
    spark.prompt_label.text = ('revert_image_url')
    pass

def config_ftp_info(spark):
    spark.prompt_label.text = ('config_ftp_info')
    pass

def change_css_theme(spark):
    spark.prompt_label.text = ('config_css_style')
    pass

def initialize_blog(spark):
    spark.prompt_label.text = ('initialize blog')
    pass