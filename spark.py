import sys
sys.path.append('./spark/modules/')
sys.path.append('./spark/pages/')

from textual.app import App
from TUI import Selector, AlertScreen
from pages import Main

class Spark(App):
    def on_mount(self):
        self.install_screen(Selector(), 'selector')
        self.install_screen(AlertScreen(), 'alert')
        self.push_screen('selector')

    def on_ready(self):
        self.main()

    def main(self):
        selector:Selector = self.screen
        selector.push_scene(Main.get_scene())
    
    def alert(self, text):
        self.push_screen('alert')
        self.screen.label.text = text
        self.app.set_focus(self.screen.button)
        selector:Selector = self.get_screen('selector')
        selector.refresh_prompt()

spark = Spark()
spark.run()
