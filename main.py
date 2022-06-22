__version__ = "1.0.8"

import json
from typing import Union

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import (
    ListProperty,
    ObjectProperty,
    ReferenceListProperty,
    StringProperty,
)
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.utils import get_color_from_hex, get_hex_from_color, platform
from kivymd.app import MDApp
from sqlitedict import SqliteDict

from config import CFG
from lightbulb import Lampada
from smartplug import Tomada

# add the following just under the imports
if platform == "android":
    from android.permissions import Permission, request_permissions

    request_permissions(
        [
            Permission.INTERNET,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
        ]
    )


class WindowManager(ScreenManager):
    pass


class HomeScreen(Screen):
    # home_screen_bg_color = ListProperty([0, 0, 0, 1])
    my_font_size = ObjectProperty()
    pass


class ColorSelectorPopup(Popup):
    pass


class ConfigScreen(Screen):
    def on_enter(self, *args) -> None:
        cfgs = App.get_running_app().my_app_cfgs
        self.form_populate()
        self.popup_color_selector = ColorSelectorPopup()
        self.popup_color_selector.color = get_color_from_hex(cfgs["lamp_color"])

    def form_populate(self) -> None:
        cfgs = App.get_running_app().my_app_cfgs
        manager = App.get_running_app().root
        manager.get_screen("config").ids.frm_lamp_enabled.active = cfgs["lamp_enabled"]
        manager.get_screen("config").ids.frm_lamp_ip.text = cfgs["lamp_ip"]
        manager.get_screen("config").ids.frm_lamp_brightness.text = cfgs[
            "lamp_brightness"
        ]
        manager.get_screen("config").ids.frm_lamp_color.text = cfgs["lamp_color"]
        manager.get_screen("config").ids.frm_powerswitch_enabled.active = cfgs[
            "powerswitch_enabled"
        ]
        manager.get_screen("config").ids.frm_powerswitch_ip.value = cfgs[
            "powerswitch_ip"
        ]
        manager.get_screen("config").ids.frm_app_timeout.value = cfgs["app_timeout"]

    def form_save(self) -> None:
        manager = App.get_running_app().root
        cfgs = {
            "lamp_enabled": manager.get_screen("config").ids.frm_lamp_enabled.active,
            "lamp_ip": manager.get_screen("config").ids.frm_lamp_ip.text,
            "lamp_brightness": int(
                manager.get_screen("config").ids.frm_lamp_brightness.value
            ),
            "lamp_color": manager.get_screen("config").ids.frm_lamp_color.text,
            "powerswitch_enabled": manager.get_screen(
                "config"
            ).ids.frm_powerswitch_enabled.active,
            "powerswitch_ip": manager.get_screen("config").ids.frm_powerswitch_ip.text,
            "app_timeout": int(manager.get_screen("config").ids.frm_app_timeout.value),
        }
        App.get_running_app().update_config_db(new_cfgs=cfgs)


class MyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.my_app_cfgs = {}
        self.lampada = None
        self.tomada = None
        self.btn_timer_state = False
        # self.lamp_state = False
        # self.power_switch_state = False
        self.event_app_timeout = None
        self.init_checks()

    def on_start(self) -> None:
        pass

    def on_end(self) -> None:
        pass

    def build(self):
        # Window.size = (400,600)
        self.title = "Sleep Color Switch App"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Purple"
        # self.theme_cls.primary_hue = "200"
        return Builder.load_file("kv/index.kv")

    def init_checks(self) -> None:
        self.load_config_db()
        self.lampada = Lampada(
            enabled=self.my_app_cfgs["lamp_enabled"], ip=self.my_app_cfgs["lamp_ip"]
        )
        self.lampada.brightness = self.my_app_cfgs["lamp_brightness"]
        self.tomada = Tomada(
            enabled=self.my_app_cfgs["powerswitch_enabled"],
            ip=self.my_app_cfgs["powerswitch_ip"],
        )
        # self.my_app_cfgs["powerswitch_enabled"] = self.tomada.is_enabled

        self.update_config_db()

    # configs
    def load_config_db(self) -> None:
        cfgs = {
            "lamp_enabled": False,
            "lamp_ip": "192.168.15.40",
            "lamp_brightness": 30,
            "lamp_color": "#00ff00",
            "powerswitch_enabled": False,
            "powerswitch_ip": "192.168.15.41",
            "app_timeout": 0,
        }
        with SqliteDict(
            CFG["DB_FILE_NAME"],
            tablename=CFG["DB_TABLE_CONFIG_NAME"],
            encode=json.dumps,
            decode=json.loads,
        ) as db:
            for k in cfgs:
                if k in db:
                    cfgs[k] = db[k]
                else:
                    db[k] = cfgs[k]
            db.commit()
        self.my_app_cfgs = cfgs

    def update_config_db(self, new_cfgs={}) -> None:
        if len(new_cfgs) == 0:
            new_cfgs = self.my_app_cfgs
        with SqliteDict(
            CFG["DB_FILE_NAME"],
            tablename=CFG["DB_TABLE_CONFIG_NAME"],
            encode=json.dumps,
            decode=json.loads,
        ) as db:
            for k in new_cfgs:
                db[k] = new_cfgs[k]
            db.commit()

        self.load_config_db()
        self.apply_app_cfgs()

    def apply_app_cfgs(self) -> None:
        if self.my_app_cfgs["lamp_enabled"]:
            self.lampada.enable()
        else:
            self.lampada.disable()
        if self.my_app_cfgs["powerswitch_enabled"]:
            self.tomada.enable()
        else:
            self.tomada.disable()
        self.lampada.brightness = self.my_app_cfgs["lamp_brightness"]
        self.lampada.color = self.my_app_cfgs["lamp_color"]

    # config > form > colorpick
    # def update_color(self, color: list) -> None:
    def update_config_frm_lamp_color(self, color: tuple) -> None:
        rgb_color = get_hex_from_color(color)
        manager = App.get_running_app().root
        manager.get_screen("config").ids.frm_lamp_color.text = rgb_color

    # plug switch
    def plug_tooggle(self) -> None:
        manager = App.get_running_app().root
        if self.my_app_cfgs["powerswitch_enabled"]:
            self.tomada.toggle()
            if self.tomada.is_on:
                manager.get_screen("home").ids.btn_power_toggle.icon = "power-plug"
            else:
                manager.get_screen("home").ids.btn_power_toggle.icon = "power-plug-off"

    def plug_off(self) -> None:
        manager = App.get_running_app().root
        if self.my_app_cfgs["powerswitch_enabled"]:
            self.tomada.turn_off()
            manager.get_screen("home").ids.btn_power_toggle.icon = "power-plug-off"

    # yeelight
    def light_toggle(self) -> None:
        manager = App.get_running_app().root
        if self.my_app_cfgs["lamp_enabled"]:
            self.lampada.toggle()
            if self.lampada.is_on:
                manager.get_screen("home").ids.btn_toggle_light.icon = "lightbulb-on"
            else:
                manager.get_screen("home").ids.btn_toggle_light.icon = "lightbulb-off"

    def light_turn_off(self) -> None:
        manager = App.get_running_app().root
        if self.my_app_cfgs["lamp_enabled"]:
            self.lampada.turn_off()
            manager.get_screen("home").ids.btn_toggle_light.icon = "lightbulb-off"

    # timer
    def start_clock(self) -> None:
        app_timeout = 0
        manager = App.get_running_app().root
        with SqliteDict(
            CFG["DB_FILE_NAME"],
            tablename=CFG["DB_TABLE_CONFIG_NAME"],
            encode=json.dumps,
            decode=json.loads,
        ) as db:
            app_timeout = db["app_timeout"]

        if app_timeout > 0:
            if not self.btn_timer_state:
                self.event_app_timeout = Clock.schedule_once(
                    lambda dt: self.end_app(), app_timeout * 60
                )  # seconds
                manager.get_screen("home").ids.btn_start_clock.icon = "clock-check"
                self.btn_timer_state = True
            else:
                Clock.unschedule(self.event_app_timeout)
                manager.get_screen("home").ids.btn_start_clock.icon = "clock"  # clock
                self.btn_timer_state = False

    def end_app(self) -> None:
        self.lampada.turn_off()
        self.tomada.turn_off()
        App.get_running_app().stop()
        Window.close()

    def test(self, *args):
        print("test()")
        # manager = App.get_running_app().root
        # print("args", args)
        # # print("manager", manager)
        # print("manager.__dict__", manager.__dict__)
        # print("manager.has_screen("home")", manager.has_screen("home"))
        # print("manager.has_screen("config")", manager.has_screen("config"))
        pass


if __name__ == "__main__":
    MyApp().run()
