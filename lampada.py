import logging
import time

# from yeelight import discover_bulbs
from yeelight import Bulb

# from yeelight import LightType
# from dataclasses import dataclass
# from pprint import pprint


"""
https://yeelight.readthedocs.io/en/latest/index.html
"""
class Lampada:
    def __init__(self, enabled, ip) -> None:
        self.light_bulb_enabled: bool = enabled
        self.auto_on: bool = True
        self.is_on: bool = False
        self.color: tuple = (35, 187, 50)
        self.ip: str = ip
        if self.light_bulb_enabled:
            self.bulb = Bulb(self.ip, auto_on=self.auto_on)

    def disable(self):
        self.light_bulb_enabled = False

    def set_rgb_from_hex(self, hex_string: str = "#FFFFFF") -> None:
        rgb = self.hex_to_rgb(hex_string)
        if self.light_bulb_enabled:
            if self.is_on is not True:
                self.turn_on()
            self.bulb.set_rgb(rgb['red'], rgb['green'], rgb['blue'])

    def turn_off(self) -> None:
        if self.light_bulb_enabled:
            self.bulb.turn_off()
            self.is_on = False

    def turn_on(self) -> None:
        if self.light_bulb_enabled:
            self.bulb.ensure_on()
            self.is_on = True

    def brightness(self, brightness: int = 50) -> None:
        if self.light_bulb_enabled:
            # if self.is_on:
            self.bulb.set_brightness(brightness)

    def hex_to_rgb(self, hex_string):
        r_hex = hex_string[1:3]
        g_hex = hex_string[3:5]
        b_hex = hex_string[5:7]
        return {
            "red": int(r_hex, 16),
            "green": int(g_hex, 16),
            "blue": int(b_hex, 16),
        }
