import numpy as np
if not hasattr(np, 'bool'):
    np.bool=bool
    np.float=float
    np.int=int
    np.complex=complex
    np.object=object

import kivy
from kivymd.app import MDApp
from kivymd.icon_definitions import md_icons
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem

import os, certifi
os.environ["SSL_CERT_FILE"]=certifi.where()
os.environ["SSL_CERT_DIR"]=os.path.dirname(certifi.where())

import weather_graph, headache_log

Builder.load_string("""
<TabbedPanelItem>:
    font_size: dp(10)
    font_name: "assets/NotoSansJP.ttf"
    color: 0.59, 0.59, 0.59, 1
    background_color: 0.25, 0.25, 0.25, 1 
    background_down: ""
    on_content: if self.content: self.content.size_hint=(1, 1)

<RootTabbedPanel>:
    do_default_tab: False
    tab_pos: "top_left"
    tab_height: dp(30) 
    tab_width: dp(70)

    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.1, 1
        Rectangle:
            pos: self.pos
            size: self.size
    TabbedPanelItem:
        text: "graph"
        content: root.get_sub1_widget()
    TabbedPanelItem:
        text: "log"
        content: root.get_sub2_widget()
""")

class MainApp(MDApp):
    def build(self):
        return RootTabbedPanel()

class RootTabbedPanel(TabbedPanel):
    def __init__(self, **kwargs):
        self.sub2_content=headache_log.headache_logApp().build()
        self.sub1_content=weather_graph.weather_graphApp().build()       
        super().__init__(**kwargs)

    def get_sub1_widget(self):
        return self.sub1_content

    def get_sub2_widget(self):
        return self.sub2_content

if __name__=="__main__":
    MainApp().run()
