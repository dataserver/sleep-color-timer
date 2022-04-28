__version__ = "1.0.1"

import json
from typing import Union

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import (ListProperty, ObjectProperty,
                             ReferenceListProperty, StringProperty)
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.pickers import MDColorPicker
from sqlitedict import SqliteDict

from lampada import Lampada
from tasmota_power_switch import PowerSwitch

DB_FILE_NAME = "data.sqlite3"
DB_TABLE_CONFIG_NAME = "configs"

class WindowManager(ScreenManager):
    pass


class HomeScreen(Screen):
    home_screen_bg_color = ListProperty([0, 0, 0, 1])
    event_app_timeout = None

    def open_color_picker(self):
        color_picker = MDColorPicker(size_hint=(0.45, 0.85))
        color_picker.open()
        color_picker.bind(
            on_select_color=self.on_select_color,
            on_release=self.get_selected_color,
        )

    def update_color(self, color: list) -> None:
        # manager = App.get_running_app().root
        # manager.get_screen("home").home_screen_bg_color = color
        self.home_screen_bg_color = color

    def get_selected_color(
                            self,
                            instance_color_picker: MDColorPicker,
                            type_color: str,
                            selected_color: Union[list, str],
                        ):
        """Return selected color."""
        # print(f"Selected color is {selected_color}")
        self.update_color(selected_color[:-1] + [1])


    def on_select_color(self, instance_gradient_tab, color: list) -> None:
        """Called when a gradient image is clicked."""
        pass




class ConfigScreen(Screen):
    def on_enter(self, *args):
        self.form_populate()

    def form_populate(self):
        cfgs =  App.get_running_app().my_app_cfgs
        manager = App.get_running_app().root
        manager.get_screen("config").ids.frm_lamp_enabled.active = cfgs["lamp_enabled"]
        manager.get_screen("config").ids.frm_lamp_ip.text = cfgs["lamp_ip"]
        manager.get_screen("config").ids.frm_lamp_brightness.text = cfgs["lamp_brightness"]
        manager.get_screen("config").ids.frm_tasmota_power_switch_enabled.active = cfgs["tasmota_power_switch_enabled"]
        manager.get_screen("config").ids.frm_tasmota_power_switch_ip.value = cfgs["tasmota_power_switch_ip"]
        manager.get_screen("config").ids.frm_app_timeout.value = cfgs["app_timeout"]

    def form_save(self):
        manager = App.get_running_app().root
        cfgs = {
            "lamp_enabled" :manager.get_screen("config").ids.frm_lamp_enabled.active,
            "lamp_ip" :manager.get_screen("config").ids.frm_lamp_ip.text,
            "lamp_brightness" : int(manager.get_screen("config").ids.frm_lamp_brightness.value),
            "tasmota_power_switch_enabled" : manager.get_screen("config").ids.frm_tasmota_power_switch_enabled.active,
            "tasmota_power_switch_ip" : manager.get_screen("config").ids.frm_tasmota_power_switch_ip.text,
            "app_timeout" : int(manager.get_screen("config").ids.frm_app_timeout.value),
        }
        App.get_running_app().update_config_db(new_cfgs=cfgs)



class MyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.my_app_cfgs = {}
        self.lampada = None
        self.power_switch = None
        self.btn_timer_state = False
        self.power_switch_state = False
        self.init_checks()

    def on_start(self) -> None:
        pass

    def on_end(self) -> None:
        pass

    def build(self):
        Window.size = (400,600)
        # self.theme_cls.theme_style = "Dark"
        # self.theme_cls.primary_palette = "Gray"
        # self.theme_cls.primary_hue = "200"
        return Builder.load_file("kv/index.kv")


    def init_checks(self) -> None:
        self.load_config_db()
        try:
            self.lampada = Lampada(enabled=self.my_app_cfgs["lamp_enabled"], ip=self.my_app_cfgs["lamp_ip"])
            self.lampada.brightness(brightness=self.my_app_cfgs["lamp_brightness"])
        except Exception as e:
            self.lampada.disable()
            self.my_app_cfgs["lamp_enabled"] = False

        self.power_switch = PowerSwitch(enabled=self.my_app_cfgs["tasmota_power_switch_enabled"], ip=self.my_app_cfgs["tasmota_power_switch_ip"])
        self.my_app_cfgs["tasmota_power_switch_enabled"] = self.power_switch.is_enabled

        self.update_config_db()

    def load_config_db(self) -> None:
        cfgs = {
                "lamp_enabled" : False,
                "lamp_ip" : "192.168.15.40",
                "lamp_brightness" : 30,
                "tasmota_power_switch_enabled" : False,
                "tasmota_power_switch_ip" : "192.168.15.41",
                "app_timeout" : 0,
            }
        with SqliteDict(DB_FILE_NAME, tablename=DB_TABLE_CONFIG_NAME, encode=json.dumps, decode=json.loads) as db:
            for k in cfgs:
                if k in db:
                    cfgs[k] = db[k]
                else:
                    db[k] = cfgs[k]
            db.commit()
        self.my_app_cfgs = cfgs

    def update_config_db(self, new_cfgs = {}) -> None:
        if len(new_cfgs) == 0:
            new_cfgs = self.my_app_cfgs
        with SqliteDict(DB_FILE_NAME, tablename=DB_TABLE_CONFIG_NAME, encode=json.dumps, decode=json.loads) as db:
            for k in new_cfgs:
                db[k] = new_cfgs[k]
            db.commit()

        self.load_config_db()
        self.apply_app_cfgs()

    def apply_app_cfgs(self) -> None:
        self.lampada.brightness(brightness=self.my_app_cfgs["lamp_brightness"])

    def toogle_power_tooggle(self, *args) -> None:
        manager = App.get_running_app().root
        if self.my_app_cfgs["tasmota_power_switch_enabled"]:
            self.power_switch.toggle()
            if self.power_switch.is_on:
                manager.get_screen("home").ids.btn_power_toggle.icon = "power-plug"
            else:
                manager.get_screen("home").ids.btn_power_toggle.icon = "power-plug-off"

    def tasmota_power_off(self, *args) -> None:
        manager = App.get_running_app().root
        if self.my_app_cfgs["tasmota_power_switch_enabled"]:
            self.power_switch.off()
            manager.get_screen("home").ids.btn_power_toggle.icon = "power-plug-off"

    def light_turn_off(self) -> None:
        self.lampada.turn_off()
        pass


    def start_clock(self) -> None:
        app_timeout = 0
        manager = App.get_running_app().root
        with SqliteDict(DB_FILE_NAME, tablename=DB_TABLE_CONFIG_NAME, encode=json.dumps, decode=json.loads) as db:
            app_timeout = db["app_timeout"]

        if app_timeout > 0:
            if not self.btn_timer_state:
                self.event_app_timeout = Clock.schedule_once(lambda dt: self.end_app(), app_timeout * 60) #seconds
                manager.get_screen("home").ids.btn_start_clock.icon = "clock-check"
                self.btn_timer_state = True
            else:
                Clock.unschedule(self.event_app_timeout)
                manager.get_screen("home").ids.btn_start_clock.icon = "clock" # clock
                self.btn_timer_state = False

    def end_app(self, *args) -> None:
        self.lampada.turn_off()
        self.tasmota_power_off()
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
