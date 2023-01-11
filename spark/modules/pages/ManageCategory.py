import sys
sys.path.append('./spark/modules/')

from TUI import Scene, Selector, get_func_names
import os

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
    contents = [filename.split('.')[0] for filename in os.listdir('./category/')]

    scene = Scene(
        main_prompt=prompt,
        contents=contents,
        multi_select=multi_select
    )

    return scene


def create_category(spark:Selector):

    def _make_category_file(spark:Selector):
        category_name = spark.get_input()

        f = open(f'./category/{category_name}.md', 'w')
        f.write(f'---\nlayout: category\ntitle: {category_name}\n---\n')
        f.close()

        os.makedirs(f'./_posts/{category_name}')

        spark.alert_line(f'Successfully created new category: {category_name}')

    spark.request_input('New Category name', callback=_make_category_file)

def rename_category(spark:Selector):
    spark.push_scene(get_category_list_scene())

    def select_callback(spark:Selector):
        item = spark.get_selected_items()
        #TODO 카테고리 이름 바꾸면서 포스팅 카테고리도 같이 변경하기


    spark.set_select_callback(select_callback, reuse=True)

def delete_category(spark:Selector):
    spark.push_scene(get_category_list_scene(prompt='Which category do you want to delete?'))

    def select_callback(spark:Selector):
        selected_category = spark.get_selected_items()[1]

        #카테고리 내 포스팅도 다 삭제할 지 물어보기
        spark.request_input('Do you want to remove all posts in the category?')
        spark.request_input()

        #선택한 카테고리 내 포스팅 내부 categories 를 uncategorized로 수정하기
        
        #포스팅모두 uncategorized 폴더로 옮기기

        #선택한 카테고리 폴더 삭제하기
        

    spark.set_select_callback(select_callback, reuse=True)



