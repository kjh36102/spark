import sys
sys.path.append('./spark/modules/')
sys.path.append('./spark/pages/')

from textual.app import App
from TUI import Selector
from pages import Main

class Spark(App):
    def on_mount(self):
        self.install_screen(Selector(), 'selector')
        self.push_screen('selector')

    def on_ready(self):
        self.main()

    def main(self):
        selector:Selector = self.screen
        selector.push_scene(Main.get_scene())

spark = Spark()
spark.run()
