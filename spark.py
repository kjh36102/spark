import sys
sys.path.append('./spark/modules/')
sys.path.append('./spark/pages/')

from TUI import TUIApp
from pages import Main

class Spark(TUIApp):
    def __init__(self):
        super().__init__()
        
    def on_ready(self):
        self.main()
        
    def main(self):
        self.push_scene(Main.get_scene())

if __name__ == '__main__':
    spark = Spark()
    spark.run()
