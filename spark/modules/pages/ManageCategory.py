import sys
sys.path.append('./spark/modules/')


from TUI import TUIApp
from TUI_DAO import Scene, get_func_names, InputRequest
from TUI_Widgets import CheckableListItem
from TUI_events import CustomProcess

import shutil
import os

class ManageCategoryProcess(CustomProcess):
    def __init__(self, app: 'TUIApp', *args) -> None:
        super().__init__(app, *args)
        
        self.funcs = [
            ManageCategoryProcess.create_category,
            ManageCategoryProcess.rename_category,
            ManageCategoryProcess.delete_category,
        ]
        
        func_names = get_func_names(self.funcs)
        
        self.scene = Scene(
            main_prompt='Manage Category',
            items=[CheckableListItem(func_name) for func_name in func_names]
        )
        
    async def main(self):
        
        while True:
            idx, val = await self.request_select(self.scene)
            await self.run(self.funcs[idx])
        
        return await super().main()
    
    async def create_category(process:CustomProcess, app:TUIApp):
        await create_category(process, app)
    
    async def rename_category(process:CustomProcess, app:TUIApp):
        pass
    
    async def delete_category(process:CustomProcess, app:TUIApp):
        # self.app.push_scene(get_category_select_scene(
        # prompt='Which category do you want to delete?'))
    
        # dup_list = [child.str for child in self.app.contents_listview.children]
    
        # idx, item = self.app.get_selected_items()
        # spark.app.alert(f'selected: {idx}, {dup_list[idx]}')
        
        # spark.remove_list_item(idx)
        # dup_list = dup_list[:idx] + dup_list[min(len(dup_list) - 1, idx + 1):]
        pass
    
    async def change_category(process:CustomProcess, app:TUIApp):
        #filepath 변수 선언하기
        
        # f = open(filepath, 'r', encoding='utf-8')
        # raw = f.read()
        # f.close()
        # raw = raw.replace('categories: [category1]', 'categories: [%s]' % category_name, 1)
        
        # f = open(filepath, 'w', encoding='utf-8')
        # f.write(raw)
        # f.close()
        pass
    

class CategorySelector(CustomProcess):
    def __init__(self, app: 'TUIApp', prompt, multi_select=False) -> None:
        super().__init__(app)
        
        categories = [filename.split('.')[0] for filename in os.listdir('./category/')]
        
        try: categories.remove('uncategorized')
        except ValueError: self.build_category_md('uncategorized')
        
        #check if there is no category
        self.scene = Scene(
            main_prompt=f'{prompt} - Select Category',
            items=[CheckableListItem(category, show_checkbox=multi_select) for category in categories],
        ) if len(categories) > 0 else None
        
    async def main(self):
        if self.scene == None:
            self.app.alert("You haven't created any categories yet.")
            self.app.pop_custom_process()
            
        idx, val = await self.request_select(self.scene)
        
        self.return_to_parent((idx, val))
        
        return await super().main()
    
    def build_category_md(category_name):
        f = open(f'./category/{category_name}.md', 'w')
        f.write(f'---\nlayout: category\ntitle: {category_name}\n---\n')
        f.close()


#-------------------------------------------------------------

async def create_category(process:CustomProcess, app:TUIApp):
    category_name = await process.request_input(
        InputRequest(prompt='Type your new category name.', hint='new category name', essential=True)
    )
    app.clear_input_box()
    
    build_category_md(category_name)
    os.makedirs(f'./_posts/{category_name}')
    app.alert(f'Successfully created new category:{category_name}.')

def rename_category(process:CustomProcess, app:TUIApp): pass

def delete_category(process:CustomProcess, app:TUIApp): pass

def change_category(process:CustomProcess, app:TUIApp): pass

    
def get_category_select_scene(prompt, multi_select=False):
    '''
    raise CustomProcess.AbortedException if there is no category else return category select scene.
    '''
    categories = [filename.split('.')[0]
                for filename in os.listdir('./category/')]
    
    try: categories.remove('uncategorized')
    except ValueError: build_category_md('uncategorized')
    
    #check if there is no category
    if len(categories) == 0: return None
        
    scene = Scene(
        main_prompt=f'{prompt} - Select Category',
        items=[CheckableListItem(category, show_checkbox=multi_select) for category in categories],
    )

    return scene

# def build_category_md(category_name):
#     f = open(f'./category/{category_name}.md', 'w')
#     f.write(f'---\nlayout: category\ntitle: {category_name}\n---\n')
#     f.close()
    