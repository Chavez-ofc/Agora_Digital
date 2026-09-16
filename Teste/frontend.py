from kivy.app import App
from kivy.lang import Builder as bd



GUI = bd.load_file("screen.kv")


class Agora (App):
    def build(self):
        return GUI

Agora().run()