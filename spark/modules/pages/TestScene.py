import sys
sys.path.append('./spark/modules/')

from TUI import Scene

LONG_STR = "It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English. Many desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for 'lorem ipsum' will uncover many web sites still in their infancy. Various versions have evolved over the years, sometimes by accident, sometimes on purpose (injected humour and the like)."

def get_scene():

    LEN = 100

    contents = [
        (f'{i}{LONG_STR}')for i in range(LEN)
    ]

    help_doc = '''\
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec finibus leo id risus efficitur efficitur. Morbi sit amet massa nibh. In porttitor elementum placerat. Vestibulum et vulputate turpis, eget ornare est. Aenean id hendrerit diam. Mauris felis ligula, malesuada eu consectetur iaculis, maximus non nunc. Pellentesque at ullamcorper nisi. Morbi viverra facilisis lacus, ac ultrices mi pellentesque id. Ut ligula dui, dictum non tempus at, vestibulum vitae purus. Integer nec ante vel nisl dictum venenatis. Duis rhoncus massa sapien, eu convallis nisl rhoncus eget. Ut consequat ante eget consectetur aliquet. Phasellus non nisi lobortis, egestas augue eu, posuere massa. Aenean molestie odio sit amet purus sollicitudin finibus. Nam consequat rutrum mi, id rutrum dui posuere elementum. Aliquam posuere ornare sodales.

Ut tincidunt sem in enim sodales mattis. Aliquam nulla sapien, tincidunt in orci et, semper accumsan odio. Pellentesque in neque nec dolor elementum tincidunt non vel nunc. Pellentesque commodo libero eget ante tempus, et efficitur nunc tincidunt. In a elit vestibulum, dictum leo id, dapibus arcu. Interdum et malesuada fames ac ante ipsum primis in faucibus. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras ac sodales arcu. Duis nibh diam, dapibus id ultrices ut, maximus et lorem. Pellentesque at mi ultricies, sodales ipsum non, dictum lorem. Vivamus finibus lacinia mauris sed blandit.

Etiam nec purus mollis felis laoreet iaculis. Maecenas est augue, ultrices dapibus nulla et, egestas dictum nisl. Maecenas tempor vestibulum nibh et eleifend. Morbi ut ante elit. Mauris a tortor lobortis, tempor lectus sit amet, efficitur enim. Donec fringilla sodales massa eu malesuada. Quisque vitae sem erat.

Nunc tristique laoreet porttitor. Sed vitae est elit. Vestibulum condimentum massa quis facilisis varius. Vestibulum sit amet dapibus magna. Proin euismod maximus libero ac egestas. Nullam nec tempus leo. Pellentesque nec ipsum dui. Ut porta, leo ac venenatis hendrerit, ipsum sem luctus sem, in ultrices tortor libero ac diam. Nam rhoncus mollis dapibus. Aenean nunc diam, volutpat at pellentesque et, lobortis eget diam. Nam semper metus id consectetur vehicula. Pellentesque quis dapibus lectus.

Duis et tortor nibh. Donec condimentum nisl nec finibus hendrerit. Cras ac elit eu urna tempus consequat at eget purus. Nulla eget arcu pretium ligula mattis lobortis. Nulla elementum vel libero non efficitur. Nulla suscipit lacinia nibh. Vivamus vehicula, metus vel luctus lacinia, lorem elit condimentum magna, vel tempus lorem leo at nisi. Integer ut nisi et dolor iaculis tincidunt sit amet eget neque.

Donec maximus metus at sollicitudin consectetur. Donec cursus aliquet massa. Phasellus orci nisi, varius nec facilisis ac, tristique a odio. Nulla vestibulum tellus mi, at convallis dolor pharetra eget. Duis venenatis eu sapien at molestie. Fusce finibus vulputate sapien vitae consequat. Nam vel ante ex. Suspendisse vitae ex molestie, ultricies lectus ut, feugiat nulla. Suspendisse convallis mauris nec ex porttitor maximus. Phasellus aliquet dolor finibus efficitur tempor. Fusce varius odio sapien, quis tincidunt nisi facilisis id. Nullam sit amet nisl efficitur, imperdiet lacus id, euismod libero. Vestibulum magna eros, facilisis vel purus eu, dictum rhoncus ante. Quisque ex leo, vulputate nec turpis vitae.
'''

    funcs = [
        (lambda x: x) for _ in range(LEN)
    ]

    func_args = [
        () for _ in range(LEN)
    ]

    scene = Scene(
        main_prompt='This is TestScene.',
        contents=contents,
        callbacks=funcs,
        callbacks_args=func_args,
        help_prompt='Need something?',
        help_doc=help_doc,
        multi_select=True
    )

    return scene

def test_func(spark):
    spark.prompt_label.text = ('create_new_post')
    pass
