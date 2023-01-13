import shutil
import os
from TUI import Scene, Selector, get_func_names
import sys
sys.path.append('./spark/modules/')


def get_scene():
    funcs = [
        create_category,
        rename_category,
        delete_category,
    ]

    func_names = get_func_names(funcs)

    scene = Scene(
        main_prompt='Manage Category',
        contents=func_names,
        callbacks=funcs,
    )

    return scene


def get_category_list_scene(prompt='Please select category.', multi_select=False):
    contents = [filename.split('.')[0]
                for filename in os.listdir('./category/')]
    
    try: contents.remove('uncategorized')
    except ValueError: build_category_md('uncategorized')
        
    scene = Scene(
        main_prompt=prompt,
        contents=contents,
        multi_select=multi_select
    )

    return scene

def build_category_md(category_name):
    f = open(f'./category/{category_name}.md', 'w')
    f.write(f'---\nlayout: category\ntitle: {category_name}\n---\n')
    f.close()

def create_category(spark: Selector):

    def _make_category_file(spark: Selector):
        category_name = spark.get_input()

        build_category_md(category_name)

        os.makedirs(f'./_posts/{category_name}')

        spark.app.alert(f'Successfully created new category:{category_name}.')

    spark.request_input(('Type your new category name.',
                        'new category name'), callback=_make_category_file)


def rename_category(spark: Selector):
    spark.push_scene(get_category_list_scene())

    def select_callback(spark: Selector):
        item = spark.get_selected_items()
        # TODO 카테고리 이름 바꾸면서 포스팅 카테고리도 같이 변경하기

    spark.set_select_callback(select_callback, reuse=True)

def change_category(filepath, category_name):
    f = open(filepath, 'r', encoding='utf-8')
    raw = f.read()
    f.close()
    raw = raw.replace('categories: [category1]', 'categories: [%s]' % category_name, 1)
    
    f = open(filepath, 'w', encoding='utf-8')
    f.write(raw)
    f.close()
    
    


def delete_category(spark: Selector):
    spark.push_scene(get_category_list_scene(
        prompt='Which category do you want to delete?'))
    
    dup_list = [child.str for child in spark.contents_listview.children]
    
    def alert_selected(spark:Selector, dup_list):
        idx, item = spark.get_selected_items()
        spark.app.alert(f'selected: {idx}, {dup_list[idx]}')
        
        spark.remove_list_item(idx)
        dup_list = dup_list[:idx] + dup_list[min(len(dup_list) - 1, idx + 1):]
        
        
    
    spark.set_select_callback(alert_selected, callback_args=(dup_list,), reuse=True)

    # def select_callback(spark: Selector):
    #     selected_idx, selected_category = spark.get_selected_items()
    #     sure_string = f"Yes I'm sure for {selected_category}"

    #     # spark.app.alert(f'selected_idx: {selected_idx}, selected_category: {selected_category}, input_buffer: {spark.selected_items}')

    #     prompt = (
    #         f'Do you want to delete all subposts within the category:{selected_category}?',
    #         f'Type "{sure_string}" to proceed.'
    #     )

    #     def request_callback(spark: Selector):
    #         typed = spark.get_input()
            
    #         category_path = f'./_posts/{selected_category}'
    #         mdfile_path = f'./category/{selected_category}.md'

    #         try:
    #             # 입력값 검사
    #             if typed == sure_string:
    #                 # 선택한 카테고리 폴더 및 파일 삭제
    #                 shutil.rmtree(category_path)
    #                 spark.app.alert(f"Category:{selected_category} and subposts deleted.")
    #             else:
    #                 # 선택한 카테고리 내 포스팅 내부 categories 를 uncategorized로 수정하기
    #                 # directory = os.fsencode(category_path)
    #                 # test = [os.fsdecode(os.path.join(directory, file))  for file in os.listdir(directory)]
    #                 # spark.app.alert(test)
                    
    #                 os.makedirs('./_posts/uncategorized', exist_ok=True)
                    
    #                 for file in os.listdir(category_path):
    #                     file_path = os.path.join(category_path, file)
    #                     change_category(f'{file_path}/{file}.md', 'uncategorized')
                            
    #                 # 포스팅모두 uncategorized 폴더로 옮기기
    #                 for dir in os.listdir(category_path):
    #                     shutil.move(os.path.join(category_path, dir), './_posts/uncategorized')

    #                 # 선택한 카테고리 폴더 삭제하기
    #                 shutil.rmtree(category_path)
                    
    #                 # spark.app.alert(f'Category:{selected_category} deleted')
                    
    #             # category폴더에서 md파일 삭제
    #             os.remove(mdfile_path)
                
    #             # spark 리스트에서 카테고리 삭제
    #             spark.remove_list_item(selected_idx)
                
    #             #포커스 설정
                
                
    #         except Exception as e:
    #             spark.app.alert(e)

    #     # 카테고리 내 포스팅도 다 삭제할 지 물어보기
    #     spark.request_input(prompt=prompt, callback=request_callback)

    # spark.set_select_callback(select_callback, reuse=True)
