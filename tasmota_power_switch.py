import requests
from requests.exceptions import JSONDecodeError

"""
https://tasmota.github.io/docs/F
"""
class PowerSwitch:
    def __init__(self, enabled, ip) -> None:
        self.is_enabled: bool = enabled
        self.is_on: bool = True
        self.ip: str = ip
        if self.is_enabled and self.ip!="":
            self.is_on = self.check_status()

    def enable(self):
        self.is_enabled = True

    def disable(self):
        self.is_enabled = False

    def check_status(self) -> bool:
        try:
            if self.is_enabled:
                r = requests.get(f"http://{self.ip}/cm?cmnd=Power")
                resp = r.json()
                self.is_on = True if resp["POWER"]=="ON" else False
        except JSONDecodeError:
            self.is_enabled = False
            self.is_on = False
        return self.is_on

    def on(self) -> None:
        try:
            if self.is_enabled:
                r = requests.get(f"http://{self.ip}/cm?cmnd=Power%20OFF")
                resp = r.json()
                self.is_on = True if resp["POWER"]=="ON" else False
        except JSONDecodeError:
            self.is_enabled = False
            self.is_on = False

    def off(self) -> None:
        try:
            if self.is_enabled:
                r = requests.get(f"http://{self.ip}/cm?cmnd=Power%20ON")
                resp = r.json()
                self.is_on = True if resp["POWER"]=="ON" else False
        except JSONDecodeError:
            self.is_enabled = False
            self.is_on = False

    def toggle(self) -> None:
        try:
            if self.is_enabled:
                r = requests.get(f"http://{self.ip}/cm?cmnd=Power%20TOGGLE")
                resp = r.json()
                self.is_on = True if resp["POWER"]=="ON" else False
        except JSONDecodeError:
            self.is_enabled = False
            self.is_on = False

