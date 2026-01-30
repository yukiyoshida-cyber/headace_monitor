from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout 
from kivymd.uix.button import MDTextButton
from kivymd.uix.label import MDLabel
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList
from kivymd.uix.screen import MDScreen
import kivy
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.lang.builder import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

import matplotlib, numpy, datetime, requests, pandas, re, os, threading, tempfile, certifi, ssl
from geopy.geocoders import Nominatim
matplotlib.use("Agg")
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

font_path="assets/NotoSansJP.ttf"
prop=fm.FontProperties(fname=font_path)
font_name=prop.get_name()
plt.rcParams["font.sans-serif"]=[font_name] + plt.rcParams["font.sans-serif"]
plt.rcParams["font.family"]="sans-serif"
plt.rcParams["axes.unicode_minus"]=False

LabelBase.register(DEFAULT_FONT, "assets/NotoSansJP.ttf")

def create_plotly_figure(stamp_df):  
    correlation_with_headache=stamp_df[[
        "headache", 
        "pressure", 
        "humidity", 
        "pressure change", 
    ]].corr()["headache"]
    correlation_plot_data=correlation_with_headache.drop("headache")
    fig, ax=plt.subplots(figsize=(9, 6))
    fig.patch.set_facecolor("#404040")
    ax.set_facecolor("#404040")
    cmap_colors=["#18ACE6", "#18ACE6", "#979797", "#979797", "#E77032", "#E77032"]
    norm_positions=[0, 0.15, 0.4, 0.6, 0.85, 1]
    custom_cmap=mcolors.LinearSegmentedColormap.from_list(
        "custom_gradient", 
        list(zip(norm_positions, cmap_colors)), 
        N=256,
    )
    norm=mcolors.Normalize(vmin=-1, vmax=1)
    colors=custom_cmap(norm(correlation_plot_data.values))
    container=ax.bar(
        correlation_plot_data.index, 
        correlation_plot_data.values, 
        color=colors, 
    )
    ax.set_ylabel(
        "correlation coefficient vs. headache", 
        color="#979797", 
        fontsize=dp(9), 
    )
    ax.set_ylim(-1.0, 1.0)
    ax.grid(axis="y")
    ax.set_xticks(
        ticks=[0, 1, 2], 
        labels=["pressure[hPa]", "humidity[%]", "pressure change[hPa/h]"], 
        rotation=dp(10), 
    )
    ax.bar_label(container, fmt="{:.2f}", color="#979797", fontsize=dp(10))
    ax.tick_params(
        axis="x", 
        color="#404040", 
        labelcolor="#979797", 
        labelsize=dp(9), 
    )
    ax.tick_params(
        axis="y", 
        color="#404040", 
        labelcolor="#979797", 
        labelsize=dp(8), 
    )
    ax.spines["bottom"].set_color("#303030")
    ax.spines["left"].set_color("#303030")
    ax.spines["right"].set_color("#303030")
    ax.spines["top"].set_color("#303030")
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#303030", alpha=0.7)
    s_m=cm.ScalarMappable(cmap=custom_cmap, norm=norm)
    s_m.set_array([])
    cbar=fig.colorbar(s_m, ax=ax, orientation="vertical", pad=0.01)
    cbar.ax.set_ylim(-1.0, 1.0)
    cbar.set_ticks([])
    cbar.ax.tick_params(length=0)
    cbar.outline.set_visible(False)
    fig=plt.gcf()
    plt.subplots_adjust(right=1.13, left=0.13, top=0.95, bottom=0.2)
    fig2=plt.figure(figsize=(10, 7))
    fig2.patch.set_facecolor("#404040")
    ax2=fig2.add_subplot(111, projection="3d")
    ax2.set_facecolor("#404040")
    norm2=mcolors.Normalize(vmin=0, vmax=5)
    cmap_colors2=["#979797", "#E77032"]
    norm_positions2=[0, 1]
    cmap2=mcolors.LinearSegmentedColormap.from_list(
        "custom_gradient", 
        list(zip(norm_positions2, cmap_colors2)), 
        N=256, 
    )
    mapper2=cm.ScalarMappable(norm=norm2, cmap=cmap2)
    colors2=[mapper2.to_rgba(value) for value in stamp_df["headache"]]
    ax2.scatter(
        stamp_df["humidity"], 
        stamp_df["pressure"], 
        stamp_df["pressure change"], 
        c=colors2, 
        marker="o", 
        s=dp(15), 
    )
    if len(stamp_df) == 1:
        ax2.set_ylim(stamp_df["pressure"].iloc[0]-1.3, stamp_df["pressure"].iloc[0]+1.3)
    ax2.xaxis.set_pane_color("#404040")
    ax2.yaxis.set_pane_color("#404040")
    ax2.zaxis.set_pane_color("#404040")
    ax2.set_xlabel("Humidity[%]", color="#979797")
    ax2.set_ylabel("Pressure[hPa]", color="#979797")
    ax2.set_zlabel("Pressure Change[hPa/h]", color="#979797")
    ax2.zaxis._axinfo["juggled"]=(1, 2, 0)
    ax2.tick_params(axis="both", labelcolor="#979797", color="#979797")
    ax2.xaxis.line.set_color("#979797")
    ax2.yaxis.line.set_color("#979797")
    ax2.zaxis.line.set_color("#979797")
    cbar=fig2.colorbar(mapper2, ax=ax2, pad=0.07, shrink=0.8)
    cbar.outline.set_visible(False)
    cbar.ax.yaxis.set_tick_params(colors="#979797")
    cbar.set_label("Headache Lebel", color="#979797")
    cbar.update_ticks()
    fig2.subplots_adjust(left=0.15, right=0.8, top=0.95, bottom=0.05)
    return fig, fig2, correlation_plot_data

kivy.require("2.3.0")

Builder.load_string(f"""
<SpinnerOption>:
    font_size:dp(12)
    size_hint_y: None
    height: dp(30)

<LastRow>:
    orientation: "horizontal"
    size_hint_x: 1
    size_hint_y: None
    height: dp(15)
    md_bg_color: [0.25, 0.25, 0.25, 1]

    MDLabel:
        text: ""
        size_hint_x: 3
        halign: "left"
    MDTextButton:
        text: " [全データ読込]"
        size_hint_x: 4
        halign: "left"
        font_size: dp(8)
        pos_hint: {{"center_y": .5}}
        theme_text_color: "Custom"
        text_color: [0.59, 0.59, 0.59, 1] 
        on_release: root.all_data_action()
    MDLabel:
        text: ""
        size_hint_x: 3

<InputPopup>:
    title: ""
    title_size: 0
    separator_height: 0

    FloatLayout:
        Label:
            size_hint: 0.8, 0.3
            pos_hint: {{"x": 0.1, "y":0.85}}
            text: root.message
            font_size: dp(12)
            halign: "center"
        BoxLayout:
            orientation: "horizontal"
            size_hint: 0.8, 0.2
            pos_hint: {{"x": 0.1, "y": 0.6}}
            Label:
                size_hint_x: 0.2
                text: "Lv: " + str(int(text_input_field.value))
                font_size: dp(12)
            Slider:
                id: text_input_field
                size_hint_x: 0.8
                min: 0
                max: 5.9
                value: 3
                cursor_height: dp(15)
                cursor_width: dp(15)
        Button:
            size_hint: 0.4, 0.2
            pos_hint: {{"x":0.1, "y":0.25}}
            text: "OK"
            font_size: dp(12)
            on_release: root.dispatch("on_yes", root.ids.text_input_field.value) 
        Button:
            size_hint: 0.4, 0.2
            pos_hint: {{"x":0.5, "y":0.25}}
            text: "Cancel"
            font_size: dp(12)
            on_release: root.dispatch("on_no")

<OkCancelPopup>:
    title: ""
    title_size: 0
    separator_height: 0

    FloatLayout:
        Label:
            size_hint: 0.8, 0.3
            pos_hint: {{"x": 0.1, "y":0.7}}
            text: root.message
            font_size: dp(12)
            halign: "center"
        Button:
            size_hint: 0.4, 0.2
            pos_hint: {{"x":0.1, "y":0.25}}
            text: "OK"
            font_size: dp(12)
            on_release: root.dispatch("on_yes")
        Button:
            size_hint: 0.4, 0.2
            pos_hint: {{"x":0.5, "y":0.25}}
            text: "Cancel"
            font_size: dp(12)
            on_release: root.dispatch("on_no")

<OkPopup>:
    title: ""
    title_size: 0
    separator_height: 0

    FloatLayout:
        Label:
            size_hint: 0.8, 0.3
            pos_hint: {{"x": 0.1, "y":0.65}}
            text: root.message
            font_size: dp(12)
            halign: "center"
        Button:
            size_hint: 0.4, 0.2
            pos_hint: {{"x":0.3, "y":0.25}}
            text: "OK"
            font_size: dp(12)
            on_release: root.dispatch("on_no")
""")

class InputPopup(Popup):
    __events__=("on_yes", "on_no")
    message=StringProperty("")

    def __init__(self, **kwargs) -> None:
        super(InputPopup, self).__init__(**kwargs)
        self.auto_dismiss=False
    
    def on_yes(self, value):
        pass
    
    def on_no(self):
        pass

class OkCancelPopup(Popup):
    __events__=("on_yes", "on_no")
    message=StringProperty("")

    def __init__(self, **kwargs) -> None:
        super(OkCancelPopup, self).__init__(**kwargs)
        self.auto_dismiss=False
    
    def on_yes(self):
        pass
    
    def on_no(self):
        pass

class OkPopup(Popup):
    __events__=("on_no", )
    message=StringProperty("")

    def __init__(self, **kwargs) -> None:
        super(OkPopup, self).__init__(**kwargs)
        self.auto_dismiss=False
    
    def on_no(self):
        pass

class DataRow(MDBoxLayout):
    datetime_str=StringProperty("")
    headache=NumericProperty(0)
    humidity=NumericProperty(0.0)
    pressure=NumericProperty(0.0)
    pressure_change=NumericProperty(0.0)
    app=ObjectProperty(None) 

    def change_action(self):
        print(f"Changed {self.datetime_str} from DataFrame.")
        target_datetime=datetime.datetime.strptime(self.datetime_str, "%Y-%m-%d %H:%M")
        self.app.target_dt=target_datetime
        if target_datetime in self.app.stamp_df.index:
            self.app.pop.message=f"""{target_datetime:%m/%d %H:%M}のLv: {int(self.app.stamp_df.loc[target_datetime, "headache"])}を
変更しますか?"""
            self.app.pop.open()
        else:
            print(f"Error: {self.datetime_str} not found in DataFrame index.")

    def delete_action(self):
        print(f"Removed {self.datetime_str} from DataFrame.")
        target_datetime=datetime.datetime.strptime(self.datetime_str, "%Y-%m-%d %H:%M")
        self.app.target_dt=target_datetime
        if target_datetime in self.app.stamp_df.index:
            self.app.delete_flg=True
            self.app.pop2.message=f"""{target_datetime:%m/%d %H:%M} Lv: {self.app.stamp_df.loc[target_datetime, "headache"]}のデータを
削除しますか?"""
            self.app.pop2.open()
        else:
            print(f"Error: {self.datetime_str} not found in DataFrame index.")

class LastRow(MDBoxLayout):
    app=ObjectProperty(None)

    def all_data_action(self):
        self.app.inner_grid.clear_widgets()
        self.app.inner_grid.add_widget(
            Label(
                text="読み込み中...", 
                font_size=dp(12), 
                color=self.app.fg_color, 
                halign="center", 
                size_hint_y=None, 
                height=dp(100), 
            ), 
        )
        Clock.schedule_once(lambda dt: self.app.update_table(self.app.stamp_df), 0.1)

class HeadacheLogLayout(BoxLayout):
    try:
        stamp_df=pandas.read_csv(
            "headache_analysis_data.csv", 
            index_col="datetime", 
            parse_dates=True, 
        )
        print(f"データを {len(stamp_df)} 件読み込みました。")
    except FileNotFoundError:
        stamp_df=pandas.DataFrame()
        print("保存されたファイルが見つかりません。新しいデータで開始します。")

    bg_color=(0.25, 0.25, 0.25, 1) # #404040
    fg_color=(0.59, 0.59, 0.59, 1) # #979797
    er_color=(0.90, 0.44, 0.20, 1) # #E77032

    jst=datetime.timezone(datetime.timedelta(hours=9), "JST")
    now=datetime.datetime.now(jst)

    location_list={
        "現在地": {"latitude": 0, "longitude": 0}, 
        "札幌駅": {"latitude": 43.0686, "longitude": 141.351}, 
        "仙台駅": {"latitude": 38.2597, "longitude": 140.883}, 
        "金沢駅": {"latitude": 36.5783, "longitude": 136.648}, 
        "東京駅": {"latitude": 35.6810, "longitude": 139.767}, 
        "新大阪駅": {"latitude": 34.7334, "longitude": 135.500}, 
        "広島駅": {"latitude": 34.3976, "longitude": 132.475}, 
        "博多駅": {"latitude": 33.5898, "longitude": 130.421}, 
        "那覇市": {"latitude": 26.2158, "longitude": 127.686}, 
    }
    location_name_list=[*location_list.keys()]

    change_flg=False
    delete_flg=False
    target_dt=None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation="vertical"
        self.padding=dp(5)
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect=Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)    
#---------------------------------------境界線border---------------------------------------
        border_frame=Widget(size_hint_y=None, height=dp(1))
        with border_frame.canvas:
            Color(*self.fg_color)
            self.border_rect=Rectangle(size=border_frame.size, pos=border_frame.pos)    
        self.add_widget(border_frame)
#---------------------------------------日時dt---------------------------------------
        dt_layout=BoxLayout(
            orientation="horizontal", 
            size_hint_y=None, 
            height=dp(55), 
            padding=(0, dp(3), 0, 0), 
        )
        dt_label=Label(
            text="日時", 
            font_size=dp(12), 
            color=self.fg_color, 
            halign="left", padding=0, 
            size_hint=(None, 1), 
            width=dp(100), 
        )
        dt_layout.add_widget(dt_label)
        dt_right_frame=BoxLayout(orientation="vertical")
        dt_term_frame=BoxLayout(
            orientation="horizontal", 
            size_hint=(None, 0.5), 
            size=(dp(300), dp(25)), 
            padding=(dp(30), 0), 
            spacing=dp(5), 
            pos_hint={"center_x": 0.5}, 
        )
        self.dt_date_entry=TextInput(
            multiline=False, 
            font_size=dp(12), 
            padding=(0, dp(3), 0, 0), 
            size_hint=(None, None), 
            size=(dp(100), dp(25)), 
            halign="center", 
            foreground_color=self.fg_color, 
            background_color=self.bg_color, 
        )
        self.dt_date_entry.bind(focus=self.update_dt_entry) 
        self.dt_date_entry.text=f"{self.now:%Y/%m/%d}"
        self.dt_time_entry=TextInput(
            multiline=False, 
            readonly=True, 
            font_size=dp(12), 
            padding=(0, dp(3), 0, 0), 
            size_hint=(None, None), 
            size=(dp(100), dp(25)), 
            halign="center", 
            foreground_color=self.fg_color, 
            background_color=self.bg_color, 
        ) 
        self.dt_time_entry.text=f"{self.now:%H}:00"
        dt_scales_frame=BoxLayout(
            orientation="horizontal", 
            size_hint=(None, 0.5), 
            size=(dp(300), dp(25)), 
            padding=(dp(17), 0), 
            spacing=dp(6), 
            pos_hint={"center_x": 0.5}, 
        )
        self.dt_date_label=Label(
            text=str(f"{0} "), 
            font_size=dp(12), 
            color=self.fg_color, 
            size_hint_x=None, 
            width=dp(7), 
        )
        self.dt_date_range=Slider(
            min=-7, 
            max=0, 
            value=0, 
            cursor_height=dp(15), 
            cursor_width=dp(15), 
            size_hint_x=None, 
            width=dp(100), 
            padding=0, 
        )
        self.dt_date_range.bind(value=self.update_dt_date)
        self.dt_time_range=Slider(
            min=0, 
            max=23, 
            value=int(f"{self.now:%H}"), 
            cursor_height=dp(15), 
            cursor_width=dp(15), 
            size_hint_x=None, 
            width=dp(100), 
            padding=0, 
        )
        self.dt_time_range.bind(value=self.update_dt_time)        
        dt_term_frame.add_widget(self.dt_date_entry)
        dt_term_frame.add_widget(self.dt_time_entry)
        dt_scales_frame.add_widget(self.dt_date_label)
        dt_scales_frame.add_widget(self.dt_date_range)
        dt_scales_frame.add_widget(self.dt_time_range)
        dt_right_frame.add_widget(dt_term_frame)
        dt_right_frame.add_widget(dt_scales_frame)
        dt_layout.add_widget(dt_right_frame)
        self.add_widget(dt_layout)
#---------------------------------------境界線border---------------------------------------
        border_frame2=Widget(size_hint_y=None, height=dp(1))
        with border_frame2.canvas:
            Color(*self.fg_color)
            self.border_rect2=Rectangle(size=border_frame2.size)    
        self.add_widget(border_frame2)
#---------------------------------------場所location---------------------------------------
        location_layout=BoxLayout(
            orientation="horizontal", 
            size_hint_y=None, 
            height=dp(45), 
            padding=(0, dp(10), dp(35), 0), 
        )        
        location_label=Label(
            text="場所", 
            font_size=dp(12), 
            color=self.fg_color, 
            halign="left", 
            padding=0, 
            size_hint=(None, 1), 
            width=dp(100), 
        )
        location_layout.add_widget(location_label)
        location_spinner_wrapper=BoxLayout(
            orientation="horizontal", 
            padding=(0, dp(10), 0, 0), 
        )
        location_spinner_wrapper=RelativeLayout()
        self.combo_var_value=self.location_name_list[0]
        self.location_spinner=Spinner(
            text=self.combo_var_value, 
            values=self.location_name_list, 
            size_hint=(None, None), 
            size=(dp(200), dp(35)), 
            pos_hint={"center_x": 0.5}, 
            font_size=dp(12), 
        )
        self.location_spinner.color=self.fg_color
        self.location_spinner.background_color=self.bg_color
        location_spinner_wrapper.add_widget(self.location_spinner)
        location_layout.add_widget(location_spinner_wrapper)
        self.add_widget(location_layout)
#---------------------------------------境界線border---------------------------------------
        border_frame3=Widget(size_hint_y=None, height=dp(1))
        with border_frame3.canvas:
            Color(*self.fg_color)
            self.border_rect3=Rectangle(size=border_frame3.size)
        self.add_widget(border_frame3)
#---------------------------------------頭痛headache---------------------------------------
        headache_layout=BoxLayout(
            orientation="horizontal", 
            size_hint_y=None, 
            height=dp(55), 
            padding=(0, dp(3), 0, 0), 
        )
        headache_label=Label(
            text="頭痛レベル", 
            font_size=dp(12), 
            color=self.fg_color, 
            halign="left", 
            padding=0, 
            size_hint=(None, 1), 
            width=dp(100), 
        )
        headache_layout.add_widget(headache_label)
        headache_right_outerframe=AnchorLayout(
            anchor_x="center", 
            anchor_y="center", 
        )
        headache_right_frame=BoxLayout(
            orientation="horizontal", 
            size_hint=(None, None), 
            size=(dp(245), dp(25)), 
        )
        self.headache_entry=TextInput(
            multiline=False, 
            readonly=True, 
            font_size=dp(12), 
            padding=(0, dp(3), 0, 0), 
            size_hint=(None, None), 
            size=(dp(20), dp(25)), 
            halign="center", 
            foreground_color=self.fg_color, 
            background_color=self.bg_color, 
        )
        self.headache_entry.text=f"3"
        self.headache_good_label=Label(
            text="  good: 0", 
            font_size=dp(12), 
            color=self.fg_color, 
            size_hint_x=None, 
            width=dp(50), 
        )
        self.headache_range=Slider(
            min=0, 
            max=5.9, 
            value=3, 
            cursor_height=dp(15), 
            cursor_width=dp(15), 
            size_hint_x=None, 
            width=dp(100), 
            padding=dp(10), 
        )
        self.headache_range.bind(value=self.update_headache)
        self.headache_bad_label=Label(
            text="wrong: 5", 
            font_size=dp(12), 
            color=self.fg_color, 
            size_hint_x=None, 
            width=dp(50), 
        )
        headache_right_frame.add_widget(self.headache_entry)
        headache_right_frame.add_widget(self.headache_good_label)
        headache_right_frame.add_widget(self.headache_range)
        headache_right_frame.add_widget(self.headache_bad_label)
        headache_right_outerframe.add_widget(headache_right_frame)
        headache_layout.add_widget(headache_right_outerframe)
        self.add_widget(headache_layout)
#---------------------------------------境界線border---------------------------------------
        border_frame4=Widget(size_hint_y=None, height=dp(1))
        with border_frame4.canvas:
            Color(*self.fg_color)
            self.border_rect4=Rectangle(size=border_frame4.size)
        self.add_widget(border_frame4)
#---------------------------------------登録entry---------------------------------------
        entry_layout=BoxLayout(
            orientation="vertical", 
            size_hint_y=None, 
            height=dp(55), 
            padding=(0, dp(10), 0, 0), 
        )
        self.entry_button=Button(
            text="登録", 
            font_size=dp(12), 
            background_normal="", 
            background_down="",
            background_color=(1, 1, 1, 0.1), 
            color=self.fg_color, 
            size_hint=(None, None), 
            size=(dp(150), dp(35)), 
            pos_hint={"center_x": 0.5},
            halign="center", 
            valign="middle", 
        )
        self.entry_button.bind(on_press=self.click_event)
        entry_layout.add_widget(self.entry_button)

        self.err_text=Label(
            text="", 
            font_size=dp(10), 
            color=self.er_color, 
            size_hint_x=None, 
            width=dp(150), 
            pos_hint={"center_x": 0.5}, 
        )
        entry_layout.add_widget(self.err_text)
        self.add_widget(entry_layout)
#---------------------------------------ポップアップpopup---------------------------------------
        self.pop=pop=InputPopup(
            message="OK ?", 
            size_hint=(0.9, 0.3), 
            pos_hint={"x":0.05, "y":0.3}, 
        )
        pop.bind(on_yes=self._popup_yes, on_no=self._popup_no)
        self.pop2=pop2=OkCancelPopup(
            message="OK ?", 
            size_hint=(0.9, 0.3), 
            pos_hint={"x":0.05, "y":0.3}, 
        )
        pop2.bind(on_yes=self._popup_yes, on_no=self._popup_no) 
        self.pop3=pop3=OkPopup(
            message="OK ?", 
            size_hint=(0.9, 0.3), 
            pos_hint={"x":0.05, "y":0.3}, 
        )
        pop3.bind(on_no=self._popup_no)
#---------------------------------------表table---------------------------------------
        self.table_layout=ScrollView(
            size_hint_y=None, 
            height=dp(100), 
            do_scroll_x=False, 
        )
        self.inner_grid=GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.inner_grid.bind(minimum_height=self.inner_grid.setter("height"))
        Builder.load_file("assets/my_layout.kv")
        df_to_process=self.stamp_df.iloc[:10] if len(self.stamp_df)>=11 else self.stamp_df
        self.update_table(df_to_process)
        self.table_layout.add_widget(self.inner_grid)
        self.add_widget(self.table_layout)
#---------------------------------------グラフgraph---------------------------------------
        self.wrap_graph_layout=ScrollView()
        self.graph_layout=BoxLayout(
            #size_hint=(None, None) if Window.width<450 else (1, None), 
            orientation="vertical", 
        )
        self.graph_layout.bind(minimum_width=self.graph_layout.setter("width"))
        self.graph_layout.bind(minimum_height=self.graph_layout.setter("height"))
        self.wrap_graph_layout.add_widget(self.graph_layout)
        self.add_widget(self.wrap_graph_layout)
        self.status_label=Label(text="", font_size=dp(30))
        self.texts=["", ".", "..", "..."]
        self.current_index=0
        self.event=None
#---------------------------------------関数---------------------------------------
    def _update_rect(self, instance, value):
        self.rect.pos=instance.pos
        self.rect.size=instance.size
        self.border_rect.pos=(
            instance.pos[0], 
            instance.pos[1]+instance.size[1]-dp(5)
        )
        self.border_rect.size=(instance.size[0], 1)
        self.border_rect2.pos=(
            instance.pos[0], 
            instance.pos[1]+instance.size[1]-dp(60)
        )
        self.border_rect2.size=(instance.size[0], 1)
        self.border_rect3.pos=(
            instance.pos[0], 
            instance.pos[1]+instance.size[1]-dp(115)
        )
        self.border_rect3.size=(instance.size[0], 1)
        self.border_rect4.pos=(
            instance.pos[0], 
            instance.pos[1]+instance.size[1]-dp(160)
        )
        self.border_rect4.size=(instance.size[0], 1)
        self.graph_layout.size_hint=(None, None) if Window.width<450 else (1, None)

    def update_dt_entry(self, instance, focus):
        if not focus:
            try:
                dt_date_text=self.dt_date_entry.text
                if re.match(r"^\d{4}/\d{2}/\d{2}$", dt_date_text):
                    dt_datetime=datetime.datetime.strptime(f"{dt_date_text} {self.dt_time_entry.text}", "%Y/%m/%d %H:%M")
                    date_difference=(dt_datetime.date() - self.now.date()).days
                    if date_difference<=self.dt_date_range.max:
                        if date_difference>=self.dt_date_range.min:
                            date_difference=date_difference
                        else:
                            date_difference=self.dt_date_range.min
                    else:
                        date_difference=self.dt_date_range.max
                    self.dt_date_range.value=0
                    self.dt_date_range.value=date_difference
                    self.dt_date_entry.foreground_color=self.fg_color
                    self.dt_time_entry.foreground_color=self.fg_color 
                else:
                    raise ValueError("日付形式が不正です")
            except Exception as e:
                instance.foreground_color=self.er_color
                print(f"Error: {e}")

    def update_dt_date(self, instance, value):
        self.dt_date_label.text=str(int(value))
        self.dt_date_entry.text=f"{self.now + datetime.timedelta(int(value)):%Y/%m/%d}"
        dt_datetime=datetime.datetime.strptime(f"{self.dt_date_entry.text} {self.dt_time_entry.text}", "%Y/%m/%d %H:%M")
        if self.now.date()==dt_datetime.date() and self.now.time()<dt_datetime.time():
            self.dt_time_range.value=int(f"{self.now:%H}")
      
    def update_dt_time(self, instance, value):
        self.dt_time_entry.text=f"{int(value):02}:00"
        dt_datetime=datetime.datetime.strptime(f"{self.dt_date_entry.text} {self.dt_time_entry.text}", "%Y/%m/%d %H:%M")
        if self.now.date()==dt_datetime.date() and self.now.time()<dt_datetime.time():
            self.dt_time_range.value=int(f"{self.now.time():%H}")
      
    def update_headache(self, instance, value):
        self.headache_entry.text=str(int(value))

    def get_data(self):
        if self.location_spinner.text=="現在地":
            response=requests.get("https://api.ipify.org")
            response=requests.get(f"http://ip-api.com/json/{response.text}")
            data=response.json()
            self.latitude=data["lat"]
            self.longitude=data["lon"]
            geolocator=Nominatim(
                user_agent="my_location_finder_app_v1", 
                ssl_context=ssl.create_default_context(cafile=certifi.where()), 
                timeout=10, 
            )
            self.location=geolocator.reverse(f"{self.latitude}, {self.longitude}", language="ja")
        else:
            self.latitude=self.location_list[self.location_spinner.text]["latitude"]
            self.longitude=self.location_list[self.location_spinner.text]["longitude"]
            geolocator=Nominatim(
                user_agent="my_location_finder_app_v1", 
                ssl_context=ssl.create_default_context(cafile=certifi.where()), 
                timeout=10, 
            )
            self.location=geolocator.reverse(
                f"{self.latitude}, {self.longitude}", 
                language="ja", 
            )
        params={
            "latitude":self.latitude, 
            "longitude":self.longitude, 
            "hourly":["relative_humidity_2m", "pressure_msl"], 
            "timezone":"Asia/Tokyo", 
            "past_days":8, 
            "forecast_days":1, 
        }
        req=requests.get("https://api.open-meteo.com/v1/forecast", params=params)
        dic=req.json()
        self.stamp_date=self.dt_date_entry.text
        self.stamp_time=self.dt_time_entry.text
        self.stamp_headache=self.headache_entry.text
        self.stamp_datetime=f"{'-'.join(self.stamp_date.split('/'))}T{self.stamp_time}"
        self.stamp_index=dic["hourly"]["time"].index(self.stamp_datetime)
        self.stamp_humidity=dic["hourly"]["relative_humidity_2m"][self.stamp_index]
        self.stamp_pressure=dic["hourly"]["pressure_msl"][self.stamp_index]
        self.stamp_pressure_change=0 if self.stamp_index==0 else dic["hourly"]["pressure_msl"][self.stamp_index]-dic["hourly"]["pressure_msl"][self.stamp_index-1]

    def add_data(self):
        self.stamp_df.loc[datetime.datetime.fromisoformat(self.stamp_datetime)]={
            "headache":int(self.stamp_headache), 
            "humidity": self.stamp_humidity, 
            "pressure": self.stamp_pressure, 
            "pressure change": self.stamp_pressure_change, 
        }
        self.stamp_df=self.stamp_df.sort_index(ascending=False)

    def update_table(self, df):
        app=MDApp.get_running_app()
        if not app or not hasattr(app, "theme_cls"):
            print("Waiting for MDApp...")
            return
        self.inner_grid.clear_widgets()
        for index, row in df.iterrows():
            item=DataRow(
                app=self, 
                datetime_str=index.strftime("%Y-%m-%d %H:%M"), 
                headache=int(row["headache"]), 
                humidity=float(row["humidity"]), 
                pressure=float(row["pressure"]), 
                pressure_change=float(row["pressure change"]), 
            )
            self.inner_grid.add_widget(item)
        if len(self.stamp_df) > len(df):
            all_data_button=LastRow(app=self)
            self.inner_grid.add_widget(all_data_button)
        self.table_layout.scroll_y=1.0

    def click_event(self, instance):
        if self.dt_date_entry.foreground_color==[*self.er_color]:
            self.err_text.text="不正入力あり"    
        else:
            self.err_text.text="" 
            instance.background_color=(0.90, 0.44, 0.20, 0.1)
            if self.event:
                self.event.cancel()
            self.current_index=0
            self.event=Clock.schedule_interval(self.update_label_text, 0.5)
            self.graph_layout.clear_widgets()
            self.graph_layout.add_widget(self.status_label)
            threading.Thread(
                target=self.generate_and_display_plot, 
                daemon=True, 
            ).start()

    def update_label_text(self, dt):
        self.status_label.text=self.texts[self.current_index]
        self.current_index+=1
        if self.current_index>=len(self.texts):
            self.current_index=0

    def generate_and_display_plot(self):
        try:
            if not (self.change_flg or self.delete_flg):
                self.get_data()
                if len(self.stamp_df)==0:
                    self.stamp_df=pandas.DataFrame({ 
                        "datetime":[datetime.datetime.fromisoformat(self.stamp_datetime)],  
                        "headache":[int(self.stamp_headache)], 
                        "humidity": [self.stamp_humidity],  
                        "pressure":[self.stamp_pressure],  
                        "pressure change": [self.stamp_pressure_change],  
                    })
                    self.stamp_df.set_index("datetime", inplace=True)
                else:
                    target_dt=pandas.Timestamp(self.stamp_datetime)
                    if target_dt in self.stamp_df.index:
                        if self.stamp_df.loc[target_dt, "headache"]!=int(self.headache_range.value):
                            self.change_flg=True
                            self.pop2.message=f"""{target_dt:%m/%d %H:%M}のLv: {self.stamp_df.loc[target_dt, "headache"]}を
Lv: {int(self.headache_range.value)}に変更しますか?"""
                            Clock.schedule_once(lambda dt: self.pop2.open(), 0)
                        else:
                            self.pop3.message=f"""{target_dt:%m/%d %H:%M} Lv: {int(self.headache_range.value)}は登録済みです"""
                            Clock.schedule_once(lambda dt: self.pop3.open(), 0)
                    else:
                        self.add_data() 
            self.stamp_df.to_csv(
                "headache_analysis_data.csv", 
                index=True, 
                encoding="utf-8", 
            )
            img_bytes=None
            self.fig, self.fig2, correlation_plot_data=create_plotly_figure(self.stamp_df)
            all_not_nan=correlation_plot_data.notna().all()
            sample_size=len(self.stamp_df)
            sample_size_flag=True
            sample_size_msg=""
            if sample_size>3 and all_not_nan:
                sample_size_msg=f"データ数: {sample_size} ※相間分析はデータが多いほど正確になります"
                img_bytes=self.fig
            else:
                sample_size_flag=False
                sample_size_msg=f"データ数: {sample_size} ※相間分析に必要なデータ数が足りません"
            Clock.schedule_once(
                lambda dt: self.update_kivy_widgets(
                    img_bytes, 
                    sample_size_flag, 
                    sample_size_msg, 
                ), 
                0, 
            )
        except Exception as e:
            print(f"Error generating plot: {e}")
            error_message=str(e)
            Clock.schedule_once(lambda dt: self.display_error(error_message), 0)

    def update_kivy_widgets(self, img_bytes, flg, msg):
        if self.event:
            self.event.cancel()
        self.graph_layout.clear_widgets()
        sample_size_msg_label=Label(
            text=msg, 
            font_size=dp(12), 
            color=self.fg_color, 
            padding=0, 
            size_hint=(1, None), 
            height=dp(10), 
        )
        self.graph_layout.add_widget(sample_size_msg_label)
        if flg:
            canvas=FigureCanvasKivyAgg(img_bytes)
            canvas.size_hint=(None, None)
            canvas.size=(dp(420), dp(260))
            canvas.pos_hint={"center_x": 0.5}
            self.graph_layout.add_widget(canvas)
        else:
            no_graph=BoxLayout(
                orientation="vertical", 
                size_hint_y=None, 
                height=dp(150), 
            )
            no_graph.add_widget(
                Label(
                    text="No Graph", 
                    font_size=dp(40), 
                    color=self.fg_color, 
                    size_hint_y=None, 
                    height=dp(80), 
                ), 
            )
            no_graph.add_widget(
                Label(
                    text="Hint: 体調がいい時は頭痛レベル0で登録", 
                    font_size=dp(10), 
                    color=self.fg_color, 
                    size_hint_y=None, 
                    height=dp(40), 
                ), 
            )
            self.graph_layout.add_widget(no_graph)
        canvas2=FigureCanvasKivyAgg(self.fig2)
        canvas2.size_hint_y=None
        canvas2.height=dp(400)
        self.graph_layout.add_widget(canvas2)
        df_to_process=self.stamp_df.iloc[:10] if len(self.stamp_df)>=11 else self.stamp_df
        self.update_table(df_to_process)
        self.entry_button.background_color=(1, 1, 1, 0.1)

    def display_error(self, message):
        if self.event:
            self.event.cancel()

        self.graph_layout.clear_widgets()
        self.graph_layout.add_widget(Label(text="Error"))
        print(f"エラー: {message}")
        self.entry_button.background_color=(1, 1, 1, 0.1)
        self.entry_button.disabled=False
      
    def _popup_yes(self, instance, *args):
        print(f"{instance} on_yes")
        if args:
            self.stamp_df.loc[self.target_dt, "headache"]=int(args[0])
            self.change_flg=True
        elif self.delete_flg:
            self.stamp_df.drop(index=self.target_dt, inplace=True)
        elif self.change_flg:
            self.stamp_df.loc[self.stamp_datetime, "headache"]=int(self.headache_range.value)
        Clock.schedule_interval(self.update_label_text, 0.5)
        self.graph_layout.clear_widgets()
        self.graph_layout.add_widget(self.status_label)
        threading.Thread(
            target=self.generate_and_display_plot, 
            daemon=True, 
        ).start()     
        self.change_flg=False
        self.delete_flg=False
        instance.dismiss()

    def _popup_no(self, instance):
        print(f"{instance} on_no")
        self.change_flg=False
        self.delete_flg=False
        instance.dismiss()

class headache_logApp(MDApp):
    def build(self):
        return HeadacheLogLayout()

if __name__=="__main__":
    headache_logApp().run()