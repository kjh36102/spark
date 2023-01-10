import sys
sys.path.append('./spark/modules/')

from TUI import Scene, Selector, get_func_names

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
        callbacks_args=[()for _ in range(len(funcs))],
    )

    return scene

def create_category(spark):
    raise ArithmeticError('create_category')
    pass

def rename_category(spark):
    raise ArithmeticError('rename_category')
    pass

def delete_category(spark):
    raise ArithmeticError('delete_category')
    pass



