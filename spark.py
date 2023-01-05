MAX_WIDTH = 50
SEP_BAR = '-' * MAX_WIDTH

def print_at(str, idx):
    print(' ' * idx + str)

def index():
    print(SEP_BAR)
    print('* WELCOME TO SPARK MANAGER *'.center(MAX_WIDTH))
    print()

    #print index
    print('[Please type number of action]')
    print('1. Config Post          | 5. Initialize blog')
    print('2. Config Category      | 6. Config Img Base URL')
    print('3. Convert Img URL      | 7. Config Disqus')
    print('4. Revert Img URL       | 8. Config CSS Style')
    print()
    return input('What would you do? >> ')

def config_post():
    pass

def config_category():
    pass

def convert_img_url():
    pass

def revert_img_url():
    pass

def initialize_blog():
    pass

def config_img_base_url():
    pass

def config_disqus():
    pass

def config_css_style():
    pass

# main -------------------------------------------
try:
    idx = index()

    if idx == '1': config_post()
    elif idx == '2': config_category()
    elif idx == '3': convert_img_url()
    elif idx == '4': revert_img_url()
    elif idx == '5': initialize_blog()
    elif idx == '6': config_img_base_url()
    elif idx == '7': config_disqus()
    elif idx == '8': config_css_style()
    else: raise IndexError('Out of selection range')

except Exception as e:
    print('!Error:', e)


