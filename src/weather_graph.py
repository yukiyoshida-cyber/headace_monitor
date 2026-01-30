from kivymd.app import MDApp
import kivy
from kivy.clock import Clock, mainthread
from kivy.core.image import Image as CoreImage
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.utils import platform

import datetime, re, numpy, requests, io, webbrowser, os, threading, tempfile, certifi, ssl
from geopy.geocoders import Nominatim
import plotly.graph_objects as go
from plotly.subplots import make_subplots

if platform=="android":
    from jnius import autoclass, cast, PythonJavaClass, java_method
    from android.runnable import run_on_ui_thread
    PythonActivity=autoclass("org.kivy.android.PythonActivity")
    WebView=autoclass("android.webkit.WebView")
    WebViewClient=autoclass("android.webkit.WebViewClient")
    Gravity=autoclass("android.view.Gravity")
    FrameLayoutLayoutParams=autoclass("android.widget.FrameLayout$LayoutParams")
    ViewGroup=autoclass("android.view.ViewGroup")
    KeyEvent=autoclass("android.view.KeyEvent")

    class KeyListener(PythonJavaClass):
        __javacontext__="app"
        __javainterfaces__=["android/view/View$OnKeyListener"]
        def __init__(self, callback):
            super().__init__()
            self.callback=callback
        @java_method("(Landroid/view/View;ILandroid/view/KeyEvent;)Z")
        def onKey(self, v, key_code, event):
            if event.getAction()==KeyEvent.ACTION_DOWN and key_code==KeyEvent.KEYCODE_BACK:
                Clock.schedule_once(lambda dt: self.callback(), 0)
                return True
            return False
else:
    def run_on_ui_thread(func):
        return func

class WebViewModal(ModalView):
    def __init__(self, html_path, **kwargs):
        kwargs.setdefault("auto_dismiss", True) 
        super(WebViewModal, self).__init__(**kwargs)
        self.html_path=html_path
        self.webview=None
        self.monitor_event=None

    def on_open(self):
        self.create_webview()
        self.monitor_event=Clock.schedule_interval(lambda dt: self.watch_webview_title(dt), 0.2)

    @run_on_ui_thread
    def watch_webview_title(self, dt):
        if self.webview:
            title=self.webview.getTitle()
            if title=="close":
                Clock.schedule_once(lambda dt: self.dismiss(), 0)

    def on_dismiss(self):
        if self.monitor_event:
            Clock.unschedule(self.monitor_event)
        self._remove_webview()

    def f2(self, *args):
        print("f2 executed")

    @run_on_ui_thread
    def create_webview(self, *args):
        activity=PythonActivity.mActivity
        self.webview=WebView(activity)
       
        s=self.webview.getSettings()
        s.setJavaScriptEnabled(True)
        s.setAllowFileAccess(True)
        s.setAllowContentAccess(True)
        s.setDomStorageEnabled(True)
       
        self.webview.setOnKeyListener(KeyListener(lambda: self.dismiss()))
       
        w=int(activity.getWindow().getDecorView().getWidth() * 0.9)
        h=int(activity.getWindow().getDecorView().getHeight() * 0.9)
        activity.addContentView(
            self.webview, 
            FrameLayoutLayoutParams(w, h, Gravity.CENTER), 
        )
        self.webview.loadUrl("file://" + self.html_path)

    @run_on_ui_thread
    def _remove_webview(self, *args):
        if self.webview:
            parent=cast(ViewGroup, self.webview.getParent())
            if parent:
                parent.removeView(self.webview)
            self.webview=None

LabelBase.register(DEFAULT_FONT, "assets/NotoSansJP.ttf")

def create_plotly_figure(
    gain_start, 
    gain_end, 
    monitor_start, 
    monitor_end, 
    latitude, 
    longitude, 
    location, 
):
    jst=datetime.timezone(datetime.timedelta(hours=9), "JST")

    params={
        "latitude":latitude, 
        "longitude":longitude, 
        "hourly":["relative_humidity_2m", 
        "pressure_msl"], 
        "timezone":"Asia/Tokyo", 
        "past_days":gain_start, 
        "forecast_days":gain_end, 
    }
    req=requests.get(
        "https://api.open-meteo.com/v1/forecast", 
        params=params,
    )
    dic=req.json()
    
    time_list=[datetime.datetime.fromisoformat(x) for x in dic["hourly"]["time"]]
    humidity_list=dic["hourly"]["relative_humidity_2m"]
    pressure_msl_list=dic["hourly"]["pressure_msl"]
    time_x=numpy.array(time_list)
    humidity_y=numpy.array(humidity_list)
    pressure_msl_y=numpy.array(pressure_msl_list)
    pressure_msl_change=pressure_msl_y[1:] - pressure_msl_y[:-1]
    pressure_msl_change=numpy.insert(pressure_msl_change, 0, 0)
    pressure_msl_change=[f"{change:+.1f} hPa/h" for change in pressure_msl_change]
    
    fig=make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=time_x, 
            y=humidity_y, 
            mode="lines", 
            name="", 
            line=dict(color="#18AEC6"), 
            hovertemplate="%{y} %", 
        ), 
        secondary_y=False, 
    )
    fig.add_trace(
        go.Scatter(
            x=time_x, 
            y=pressure_msl_y, 
            mode="lines", 
            name="", 
            customdata=pressure_msl_change, 
            line=dict(color="#E77032"), 
            hovertemplate="%{y} hPa<br>%{customdata}", 
        ), 
        secondary_y=True, 
    )
    fig.update_layout(
        plot_bgcolor="#404040", 
        paper_bgcolor="#404040", 
        font=dict(color="#979797"), 
        hovermode="x unified", 
        margin=dict(t=45, l=0, r=0, b=0), 
        title_font=dict(size=14), 
        title_text=f"{location} ", 
        showlegend=False, 
        xaxis=dict(
            range=[monitor_start, monitor_end], 
            showspikes=True, 
            spikemode="across", 
            spikesnap="cursor", 
            spikecolor="#979797", 
            spikedash="solid", 
            spikethickness=2, 
        ), 
    )
    fig.update_yaxes(
        title_text="Humidity [%]", 
        secondary_y=False, 
        showgrid=False, 
        color=fig.data[0].line.color, 
        title_font=dict(color=fig.data[0].line.color), 
    )
    fig.update_yaxes(
        title_text="Pressure MSL [hPa]", 
        secondary_y=True, 
        showgrid=False, 
        color=fig.data[1].line.color, 
        title_font=dict(color=fig.data[1].line.color), 
    )
    fig.update_xaxes(
        tickformat="%m/%d(%a) \n%H:%M", 
        hoverformat="%m/%d(%a) %H:%M", 
        gridcolor="#979797", 
        gridwidth=1.5, 
        minor=dict(
            showgrid=True, 
            gridcolor="#979797", 
            gridwidth=0.5, 
            griddash="dot", 
            dtick=21600000, 
        ), 
    )
    fig.add_shape(
        type="line", 
        xref="x", 
        layer="below", 
        yref="paper", 
        x0=datetime.datetime.now(jst), 
        y0=0, 
        x1=datetime.datetime.now(jst), 
        y1=1, 
        line=dict(color="#979797", width=3, dash="dash"), 
    )
    return fig

def get_plot_image_bytes(fig):
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".html", delete=False) as f:
        html_filepath=f.name
    if platform=="android":
        from bs4 import BeautifulSoup
        file_name=os.path.basename(html_filepath)
        html_filepath=os.path.join(
            MDApp.get_running_app().user_data_dir, 
            file_name, 
        )
        fig.write_html(html_filepath)
        with open(html_filepath, "r", encoding="utf-8") as f:
            soup=BeautifulSoup(f, "html.parser")
        btn_html="""
            <div id="close-btn" 
            onclick="document.title='close';"
            style="position: fixed;
                top: 10px; 
                right: 10px; 
                z-index: 9999;
                width: 30px; 
                height: 30px; 
                background: rgba(0, 0, 0, 0.5);
                color: white; 
                border-radius: 50%; 
                text-align: center;
                line-height: 30px; 
                font-size: 30px; 
                font-family: 
                sans-serif;
                cursor: pointer;"
            >&times;</div>
        """
        soup.body.append(BeautifulSoup(btn_html, "html.parser"))
        with open(html_filepath, "w", encoding="utf-8") as f:
            f.write(str(soup))
        return [None, html_filepath]  
    else:
        fig.write_html(html_filepath)
        buf=io. BytesIO()
        fig.update_layout(title_font=dict(size=dp(28)), margin=dict(t=dp(80)))
        fig.update_xaxes(tickformat="%m/%d \n%H:%M", tickfont=dict(size=dp(18)))
        fig.update_yaxes(
            secondary_y=False, 
            title_font=dict(size=dp(20)), 
            tickfont=dict(size=dp(20)), 
        )
        fig.update_yaxes(
            secondary_y=True, 
            title_font=dict(size=dp(20)), 
            tickfont=dict(size=dp(20)), 
        )
        fig.write_image(buf, format="png", width=dp(750), height=dp(750))
        buf.seek(0)
        return [buf.getvalue(), html_filepath]

kivy.require("2.3.0")

Builder.load_string(f"""
<SpinnerOption>:
    font_size:dp(12)
    size_hint_y: None
    height: dp(30)
""")

class weather_graphApp(MDApp):
    bg_color=(0.25, 0.25, 0.25, 1) # #404040
    fg_color=(0.59, 0.59, 0.59, 1) # #979797
    er_color=(0.90, 0.44, 0.20, 1) # #E77032

    jst=datetime.timezone(datetime.timedelta(hours=9), "JST")
    now=datetime.datetime.now(jst)

    gain_start_var=NumericProperty(-7)
    gain_end_var=NumericProperty(7)
    gain_start_date_str=StringProperty("")
    gain_end_date_str=StringProperty("")

    monitor_start_var=NumericProperty(-1)
    monitor_end_var=NumericProperty(3)
    monitor_start_date_str=StringProperty("")
    monitor_end_date_str=StringProperty("")
    
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

    def build(self):
        self.root=FloatLayout() 
        Clock.schedule_once(self.delayed_init, 0.1)
        return self.root

    def delayed_init(self, dt):
        main_layout=BoxLayout(orientation="vertical", padding=dp(5))
        with main_layout.canvas.before:
            Color(*self.bg_color)
            self.rect=Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self._update_rect, pos=self._update_rect)        
#---------------------------------------境界線border---------------------------------------
        border_frame=Widget(size_hint_y=None, height=dp(1))
        with border_frame.canvas:
            Color(*self.fg_color)
            self.border_rect=Rectangle(
                size=border_frame.size, 
                pos=border_frame.pos, 
            )       
        main_layout.add_widget(border_frame)
#---------------------------------------情報取得期間gain---------------------------------------
        gain_layout=BoxLayout(
            orientation="horizontal", 
            size_hint_y=None, 
            height=dp(55), 
            padding=(0, dp(3), 0, 0), 
        )
        gain_label=Label(
            text="情報取得期間", 
            font_size=dp(12), 
            color=self.fg_color, 
            halign="left", 
            padding=0, 
            size_hint=(None,1), 
            width=dp(100), 
        )
        gain_layout.add_widget(gain_label)
        gain_right_frame=BoxLayout(orientation="vertical")
        self.gain_start_date_str=f"{self.now + datetime.timedelta(days=self.gain_start_var):%Y/%m/%d}"
        self.gain_end_date_str=f"{self.now + datetime.timedelta(days=self.gain_end_var):%Y/%m/%d}"
        gain_term_frame=BoxLayout(
            orientation="horizontal", 
            size_hint=(None, 0.5), 
            size=(dp(300), dp(25)), 
            padding=(dp(35), 0), 
            pos_hint={"center_x": 0.5}, 
        )
        self.gain_start_entry=TextInput(
            multiline=False, 
            font_size=dp(12), 
            padding=(0, dp(3), 0, 0), 
            size_hint=(None, None), 
            size=(dp(100), dp(25)), 
            halign="center", 
            foreground_color=self.fg_color, 
            background_color=self.bg_color, 
        )
        self.gain_start_entry.bind(focus=self.update_gain_entry) 
        self.gain_start_entry.text=self.gain_start_date_str
        term_label=Label(
            text="~", 
            font_size=dp(15),  
            color=self.fg_color, 
            size_hint_x=None, 
            width=dp(20), 
        )
        self.gain_end_entry=TextInput(
            multiline=False, 
            font_size=dp(12), 
            padding=(0, dp(3), 0, 0), 
            size_hint=(None, None), 
            size=(dp(100), dp(25)), 
            halign="center", 
            foreground_color=self.fg_color, 
            background_color=self.bg_color, 
        )
        self.gain_end_entry.bind(focus=self.update_gain_entry)
        self.gain_end_entry.text=self.gain_end_date_str
        gain_term_frame.add_widget(self.gain_start_entry)
        gain_term_frame.add_widget(term_label)
        gain_term_frame.add_widget(self.gain_end_entry)
        gain_right_frame.add_widget(gain_term_frame)
        gain_scales_frame=BoxLayout(
            orientation="horizontal", 
            size_hint=(None, 0.5), 
            size=(dp(300), dp(25)), 
            padding=(dp(20), 0), 
            pos_hint={"center_x": 0.5}, 
        )
        self.gain_start_label=Label(
            text=str(self.gain_start_var), 
            font_size=dp(12), 
            color=self.fg_color, 
            size_hint_x=None, 
            width=dp(3), 
        )
        self.gain_start_range=Slider(
            min=-30, 
            max=-1, 
            value=self.gain_start_var, 
            cursor_height=dp(15), 
            cursor_width=dp(15), 
            size_hint_x=None, 
            width=dp(120), 
            padding=dp(10), 
        )
        self.gain_start_range.bind(value=self.update_gain_start)
        gain_space_label=Label(text="", size_hint_x=None, width=dp(2)) 
        gain_scales_frame.add_widget(self.gain_start_label)
        gain_scales_frame.add_widget(self.gain_start_range)
        gain_scales_frame.add_widget(gain_space_label)
        self.gain_end_range=Slider(
            min=1, 
            max=16, 
            value=self.gain_end_var, 
            cursor_height=dp(15), 
            cursor_width=dp(15), 
            size_hint_x=None, 
            width=dp(120), 
            padding=dp(10), 
        )
        self.gain_end_range.bind(value=self.update_gain_end)
        self.gain_end_label=Label(
            text=str(self.gain_end_var), 
            font_size=dp(12), 
            color=self.fg_color, 
            size_hint_x=None, 
            width=dp(3), 
        )
        gain_scales_frame.add_widget(self.gain_end_range)
        gain_scales_frame.add_widget(self.gain_end_label)
        gain_right_frame.add_widget(gain_scales_frame)        
        gain_layout.add_widget(gain_right_frame)
        main_layout.add_widget(gain_layout)
#---------------------------------------境界線border---------------------------------------
        border_frame2=Widget(size_hint_y=None, height=dp(1))
        with border_frame2.canvas:
            Color(*self.fg_color)
            self.border_rect2=Rectangle(size=border_frame2.size)
        main_layout.add_widget(border_frame2)
#---------------------------------------初期表示期間monitor---------------------------------------
        monitor_layout=BoxLayout(
            orientation="horizontal", 
            size_hint_y=None, 
            height=dp(60), 
        )
        monitor_label=Label(
            text="初期表示期間", 
            font_size=dp(12), 
            color=self.fg_color, 
            halign="left", 
            padding=0, 
            size_hint=(None, 1), 
            width=dp(100),
        )
        monitor_layout.add_widget(monitor_label)
        monitor_right_frame=BoxLayout(orientation="vertical")
        self.monitor_start_date_str=f"{self.now + datetime.timedelta(days=self.monitor_start_var):%Y/%m/%d}"
        self.monitor_end_date_str=f"{self.now + datetime.timedelta(days=self.monitor_end_var):%Y/%m/%d}"
        monitor_term_frame=BoxLayout(
            orientation="horizontal", 
            size_hint=(None, None),  
            size=(dp(300), dp(20)), 
            padding=(dp(35), 0), 
            pos_hint={"center_x": 0.5}, 
        )
        self.monitor_start_entry=TextInput( 
            multiline=False,  
            font_size=dp(12),  
            padding=(0, dp(3), 0, 0),  
            size_hint=(None, None),  
            size=(dp(100), dp(25)),  
            halign="center",  
            foreground_color=self.fg_color,  
            background_color=self.bg_color, 
        )
        self.monitor_start_entry.bind(focus=self.update_monitor_entry) 
        self.monitor_start_entry.text=self.monitor_start_date_str
        term_label=Label( 
            text="~",  
            font_size=dp(15),  
            color=self.fg_color,  
            size_hint_x=None,  
            width=dp(20), 
        )
        self.monitor_end_entry=TextInput( 
            multiline=False,  
            font_size=dp(12),  
            padding=(0, dp(3), 0, 0),  
            size_hint=(None, None),  
            size=(dp(100), dp(25)),  
            halign="center",  
            foreground_color=self.fg_color,  
            background_color=self.bg_color, 
        )
        self.monitor_end_entry.bind(focus=self.update_monitor_entry)
        self.monitor_end_entry.text=self.monitor_end_date_str
        monitor_term_frame.add_widget(self.monitor_start_entry)
        monitor_term_frame.add_widget(term_label)
        monitor_term_frame.add_widget(self.monitor_end_entry)
        monitor_right_frame.add_widget(monitor_term_frame)
        monitor_scales_frame=BoxLayout( 
            orientation="horizontal",  
            size_hint=(None, None),  
            size=(dp(300), dp(25)), 
            padding=(dp(20), 0),  
            pos_hint={"center_x": 0.5}, 
        )
        self.monitor_start_label=Label(
            text=str(self.monitor_start_var), 
            font_size=dp(12), 
            color=self.fg_color, 
            size_hint_x=None, 
            width=dp(3), 
        )
        self.monitor_start_range=Slider(
            min=-7, 
            max=-1, 
            value=self.monitor_start_var, 
            cursor_height=dp(15), 
            cursor_width=dp(15), 
            size_hint_x=None, 
            width=dp(120), 
            padding=dp(10), 
        )
        self.monitor_start_range.bind(value=self.update_monitor_start)
        monitor_space_label=Label(text="", size_hint_x=None,  width=dp(2)) 
        monitor_scales_frame.add_widget(self.monitor_start_label)
        monitor_scales_frame.add_widget(self.monitor_start_range)
        monitor_scales_frame.add_widget(monitor_space_label)
        self.monitor_end_range=Slider(
            min=1, 
            max=7, 
            value=self.monitor_end_var, 
            cursor_height=dp(15), 
            cursor_width=dp(15), 
            size_hint_x=None, 
            width=dp(120), 
            padding=dp(10), 
        )
        self.monitor_end_range.bind(value=self.update_monitor_end)
        self.monitor_end_label=Label(
            text=str(self.monitor_end_var), 
            font_size=dp(12), 
            color=self.fg_color, 
            size_hint_x=None, 
            width=dp(3), 
        )
        monitor_scales_frame.add_widget(self.monitor_end_range)
        monitor_scales_frame.add_widget(self.monitor_end_label)
        monitor_right_frame.add_widget(monitor_scales_frame)
        monitor_layout.add_widget(monitor_right_frame)
        main_layout.add_widget(monitor_layout)
#---------------------------------------境界線border---------------------------------------
        border_frame3=Widget(size_hint_y=None, height=dp(1))
        with border_frame3.canvas:
            Color(*self.fg_color)
            self.border_rect3=Rectangle(size=border_frame3.size)
        main_layout.add_widget(border_frame3)
#---------------------------------------場所location---------------------------------------
        location_layout=BoxLayout(
            orientation="horizontal", 
            size_hint_y=None, 
            height=dp(45), 
            padding=(0, dp(10), 0, 0), 
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
        main_layout.add_widget(location_layout)
#---------------------------------------境界線border---------------------------------------
        border_frame4=Widget(size_hint_y=None, height=dp(1))
        with border_frame4.canvas:
            Color(*self.fg_color)
            self.border_rect4=Rectangle(size=border_frame4.size)
        main_layout.add_widget(border_frame4)
#---------------------------------------更新update---------------------------------------
        update_layout=BoxLayout(
            orientation="vertical", 
            size_hint_y=None, 
            height=dp(55), 
            padding=(0, dp(10), 0, 0), 
        )
        self.update_button=Button(
            text="更新", 
            font_size=dp(12), 
            background_normal="", 
            background_down="", 
            background_color=(1, 1, 1, 0.1), 
            color=self.fg_color, 
            size_hint=(None, None), 
            size=(dp(150), dp(35)),
            pos_hint={"center_x": 0.5}, 
            halign="center", valign="middle", 
        )
        self.update_button.bind(on_press=self.click_event)
        update_layout.add_widget(self.update_button)
        self.kivy_view=None
        self.err_text=Label(
            text="", 
            font_size=dp(10), 
            color=self.er_color, 
            size_hint_x=None, 
            width=dp(150), 
            pos_hint={"center_x": 0.5}, 
        )
        update_layout.add_widget(self.err_text)
        main_layout.add_widget(update_layout)
#---------------------------------------グラフgraph---------------------------------------
        self.graph_layout=BoxLayout(
            orientation="vertical", 
            padding=0, 
            spacing=dp(10), 
        )
        main_layout.add_widget(self.graph_layout)
        self.status_label=Label(text="", font_size=dp(30))
        self.texts=["", ".", "..", "..."]
        self.current_index=0
        self.event=None
        self.root.add_widget(main_layout)
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
            instance.pos[1]+instance.size[1]-dp(65)
        )
        self.border_rect2.size=(instance.size[0], 1)
        self.border_rect3.pos=(
            instance.pos[0], 
            instance.pos[1]+instance.size[1]-dp(125)
        )
        self.border_rect3.size=(instance.size[0], 1)
        self.border_rect4.pos=(
            instance.pos[0], 
            instance.pos[1]+instance.size[1]-dp(175)
        )
        self.border_rect4.size=(instance.size[0], 1)

    def update_gain_start(self, instance, value):
        self.gain_start_var=int(value)
        self.gain_start_label.text=str(self.gain_start_var)
        self.gain_start_entry.text=f"{self.now + datetime.timedelta(days=self.gain_start_var):%Y/%m/%d}"
        self.monitor_start_range.min=self.gain_start_var
        
    def update_gain_end(self, instance, value):
        self.gain_end_var=int(value)
        self.gain_end_label.text=str(self.gain_end_var)
        self.gain_end_entry.text=f"{self.now + datetime.timedelta(days=self.gain_end_var):%Y/%m/%d}"
        self.monitor_end_range.max=self.gain_end_var

    def update_gain_entry(self, instance, focus):
        if not focus:
            try:
                start_text=self.gain_start_entry.text
                end_text=self.gain_end_entry.text
                if re.match(r"^\d{4}/\d{2}/\d{2}$", start_text) and re.match(r"^\d{4}/\d{2}/\d{2}$", end_text):
                    gain_start_date=datetime.datetime.strptime(start_text, "%Y/%m/%d").date()
                    gain_end_date=datetime.datetime.strptime(end_text, "%Y/%m/%d").date()
                    today_date=self.now.date()
                    gain_start_difference=(gain_start_date - today_date).days
                    if gain_start_difference<=self.gain_start_range.max:
                        if gain_start_difference>=self.gain_start_range.min:
                            gain_start_difference=gain_start_difference
                        else:
                            gain_start_difference=self.gain_start_range.min
                    else:
                        gain_start_difference=self.gain_start_range.max
                    print(gain_start_difference)
                    gain_end_difference=(gain_end_date - today_date).days
                    if gain_end_difference<=self.gain_end_range.max:
                        if gain_end_difference>=self.gain_end_range.min:
                            gain_end_difference=gain_end_difference
                        else:
                            gain_end_difference=self.gain_end_range.min
                    else:
                        gain_end_difference=self.gain_end_range.max
                    self.gain_start_range.value=0
                    self.gain_start_range.value=gain_start_difference
                    self.gain_end_range.value=0
                    self.gain_end_range.value=gain_end_difference
                    self.gain_start_entry.foreground_color=self.fg_color
                    self.gain_end_entry.foreground_color=self.fg_color
                else:
                    raise ValueError("日付形式が不正です")
            except Exception as e:
                instance.foreground_color=self.er_color
                print(f"Error: {e}")

    def update_monitor_start(self, instance, value):
        self.monitor_start_var=int(value)
        self.monitor_start_label.text=str(self.monitor_start_var)
        self.monitor_start_entry.text=f"{self.now + datetime.timedelta(days=self.monitor_start_var):%Y/%m/%d}"

    def update_monitor_end(self, instance, value):
        self.monitor_end_var=int(value)
        self.monitor_end_label.text=str(self.monitor_end_var)
        self.monitor_end_entry.text=f"{self.now + datetime.timedelta(days=self.monitor_end_var):%Y/%m/%d}"

    def update_monitor_entry(self, instance, focus):
        if not focus:
            try:
                start_text=self.monitor_start_entry.text
                end_text=self.monitor_end_entry.text
                if re.match(r"^\d{4}/\d{2}/\d{2}$", start_text) and re.match(r"^\d{4}/\d{2}/\d{2}$", end_text):
                    monitor_start_date=datetime.datetime.strptime(start_text, "%Y/%m/%d").date()
                    monitor_end_date=datetime.datetime.strptime(end_text, "%Y/%m/%d").date()
                    today_date=self.now.date()
                    monitor_start_difference=(monitor_start_date - today_date).days
                    if monitor_start_difference<=self.monitor_start_range.max:
                        if monitor_start_difference>=self.monitor_start_range.min:
                            monitor_start_difference=monitor_start_difference
                        else:
                            monitor_start_difference=self.monitor_start_range.min
                    else:
                        monitor_start_difference=self.monitor_start_range.max
                    monitor_end_difference=(monitor_end_date - today_date).days
                    if monitor_end_difference<=self.monitor_end_range.max:
                        if monitor_end_difference>=self.monitor_end_range.min:
                            monitor_end_difference=monitor_end_difference
                        else:
                            monitor_end_difference=self.monitor_end_range.min
                    else:
                        monitor_end_difference=self.monitor_end_range.max
                    self.monitor_start_range.value=0
                    self.monitor_start_range.value=monitor_start_difference
                    self.monitor_end_range.value=0
                    self.monitor_end_range.value=monitor_end_difference
                    self.monitor_start_entry.foreground_color=self.fg_color
                    self.monitor_end_entry.foreground_color=self.fg_color
                else:
                    raise ValueError("日付形式が不正です")
            except Exception as e:
                instance.foreground_color=self.er_color
                print(f"Error: {e}")

    def click_event(self, instance):
        if (self.gain_start_entry.foreground_color==[*self.er_color] or
            self.gain_end_entry.foreground_color==[*self.er_color] or
            self.monitor_start_entry.foreground_color==[*self.er_color] or
            self.monitor_end_entry.foreground_color==[*self.er_color]):
            self.err_text.text="不正入力あり"       
        else:
            self.err_text.text="" 
            instance.background_color=(0.90, 0.44, 0.20, 0.1)
            instance.text="更新中"
            if self.event:
                self.event.cancel()
            self.current_index=0
            self.event=Clock.schedule_interval(self.update_label_text, 0.5)
            self.graph_layout.clear_widgets()
            self.graph_layout.add_widget(self.status_label)
            threading.Thread(
                target=self.generate_and_display_plot, 
                daemon=True
            ).start()

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
            self.location=geolocator.reverse(
                f"{self.latitude}, {self.longitude}", 
                language="ja", 
            )
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
        self.gain_start=self.gain_start_var*-1
        self.gain_end=self.gain_end_var
        self.monitor_start=self.now.replace(hour=0, minute=0)+datetime.timedelta(days=self.monitor_start_var)
        self.monitor_end=self.now.replace(hour=0, minute=0)+datetime.timedelta(days=self.monitor_end_var)
        print(f"""
            gain:- {self.gain_start} ~ + {self.gain_end}
            monitor:{self.monitor_start} ~ {self.monitor_end}
            location:{self.location}, latitude:{self.latitude}, longitude:{self.longitude}""")

    def update_label_text(self, dt):
        self.status_label.text=self.texts[self.current_index]
        self.current_index+=1
        if self.current_index>=len(self.texts):
            self.current_index=0

    def generate_and_display_plot(self):
        try:
            self.get_data()
            self.fig=create_plotly_figure(
                self.gain_start, 
                self.gain_end, 
                self.monitor_start, 
                self.monitor_end, 
                self.latitude, 
                self.longitude, 
                self.location, 
            )
            img_bytes, self.html_filepath=get_plot_image_bytes(self.fig)
            Clock.schedule_once(lambda dt: self.update_kivy_widgets(img_bytes), 0)
        except Exception as e:
            print(f"Error generating plot: {e}")
            error_message=str(e)
            Clock.schedule_once(lambda dt: self.display_error(error_message), 0)

    def update_kivy_widgets(self, img_bytes):
        if self.event:
            self.event.cancel()
        self.graph_layout.clear_widgets()
        if platform=="android":
            wm=WebViewModal(html_path=self.html_filepath, size_hint=(0.9, 0.9))
            wm.open()
        else:
            ci=CoreImage(io.BytesIO(img_bytes), ext="png")
            self.plot_image_widget=Image(texture=ci.texture, size_hint_y=0.8)
            self.graph_layout.add_widget(self.plot_image_widget)
            self.detail_button=Button(
                text="詳細(ブラウザ)", 
                font_size=dp(12), 
                background_normal="", 
                background_down="", 
                background_color=(1, 1, 1, 0.1), 
                color=self.fg_color, 
                size_hint_y=None, 
                height=dp(35), 
                pos_hint={"center_x": 0.5}, 
                on_press=self.open_plotly_html, 
            )
            self.graph_layout.add_widget(self.detail_button)
        self.update_button.background_color=(1, 1, 1, 0.1)
        self.update_button.text="更新"

    def display_error(self, message):
        if self.event:
            self.event.cancel()
        self.graph_layout.clear_widgets()
        self.graph_layout.add_widget(Label(text=f"Error"))
        print(f"エラー: {message}")
        self.update_button.background_color=(1, 1, 1, 0.1)
        self.update_button.text="更新"
        self.update_button.disabled=False

    def open_plotly_html(self, instance):
        instance.background_color=(0.90, 0.44, 0.20, 0.1)
        threading.Thread(target=self.show_html, daemon=True).start()

    def show_html(self):
        if hasattr(self, "fig"):
            webbrowser.open(f"file://{os.path.realpath(self.html_filepath)}")        
        Clock.schedule_once(
            lambda dt: setattr(
                self.detail_button, 
                "background_color", 
                (1, 1, 1, 0.1), 
            ), 
            0, 
          )

if __name__=="__main__":
    weather_graphApp().run()