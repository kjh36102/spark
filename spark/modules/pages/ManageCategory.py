import sys
sys.path.append('./spark/modules/')
sys.path.append('./spark/modules/pages/')

from TUI import *
from TUI_DAO import *

import shutil
import os

class ManageCategoryProcess(CustomProcess):
    def __init__(self, app: 'TUIApp') -> None:
        super().__init__(app)
        
        self.funcs = [
            self.create_category,
            self.rename_category,
            self.delete_category,
            self.change_category
        ]
        
        func_names = get_func_names(self.funcs)
        
        self.scene = Scene(
            main_prompt='Manage Category',
            items=func_names
        )
        
    async def main(self):
        idx, val = await self.request_select(self.scene)
        await self.funcs[idx]()
        
    
    async def create_category(self):
        await create_category(self, self.app)
    
    async def rename_category(self):
        pass
    
    async def delete_category(self):
        # self.app.push_scene(get_category_select_scene(
        # prompt='Which category do you want to delete?'))
    
        # dup_list = [child.str for child in self.app.contents_listview.children]
    
        # idx, item = self.app.get_selected_items()
        # spark.app.alert(f'selected: {idx}, {dup_list[idx]}')
        
        # spark.remove_list_item(idx)
        # dup_list = dup_list[:idx] + dup_list[min(len(dup_list) - 1, idx + 1):]
        pass
    
    async def change_category(self):
        #filepath 변수 선언하기
        
        # f = open(filepath, 'r', encoding='utf-8')
        # raw = f.read()
        # f.close()
        # raw = raw.replace('categories: [category1]', 'categories: [%s]' % category_name, 1)
        
        # f = open(filepath, 'w', encoding='utf-8')
        # f.write(raw)
        # f.close()
        pass



#-------------------------------------------------------------


async def create_category(process:CustomProcess, app:TUIApp):
    category_name = await process.request_input(
        InputRequest(
            prompt='Type your new category name.',
            hint='new category name',
            essential=True
        )
    )
    
    build_category_md(category_name)
    os.makedirs(f'./_posts/{category_name}', exist_ok=True)
    app.alert(f'Successfully created new category:{category_name}.')

def rename_category(process:CustomProcess, app:TUIApp): pass

def delete_category(process:CustomProcess, app:TUIApp): pass

def change_category(process:CustomProcess, app:TUIApp): pass

def get_category_select_scene(prompt, multi_select=False):

    category_dir_path = './category'
    os.makedirs(category_dir_path, exist_ok=True)

    category_list = os.listdir(category_dir_path)

    # app.print_log('category list:', category_list)

    categories = [filename.split('.')[0] for filename in category_list]

    try: categories.remove('uncategorized')
    except ValueError: build_category_md('uncategorized')
    
    #check if there is no category
    scene = Scene(
        main_prompt=f'{prompt} - Select Category',
        items=categories,
        multi_select=multi_select
    ) if len(categories) > 0 else None

    return scene

def build_category_md(category_name):
    f = open(f'./category/{category_name}.md', 'w')
    f.write(f'---\nlayout: category\ntitle: {category_name}\n---\n')
    f.close()