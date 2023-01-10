import sys
sys.path.append('./spark/modules/')
sys.path.append('./spark/pages/')

from TUI2 import Selector, App
from pages import Main
from pages import TestScene

class Spark(App):
    def on_mount(self):
        self.install_screen(Selector(), 'selector')
        self.push_screen('selector')

    def on_ready(self):
        self.main()

    def main(self):
        selector:Selector = self.screen
        selector.push_scene(TestScene.get_scene())

spark = Spark()
spark.run()
