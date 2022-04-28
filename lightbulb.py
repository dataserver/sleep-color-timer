from yeelight import Bulb

"""
https://yeelight.readthedocs.io/en/latest/index.html
"""
class Lampada:
    def __init__(self, enabled, ip) -> None:
        self._is_enabled: bool = enabled
        self._is_available: bool = False
        self._is_on: bool = False
        self._color: str = "#FFCCFF"
        self._brightness = 50
        self._ip: str = ip
        self._check_status()

    def _check_status(self) -> None:
        try:
            if self._is_enabled:
                self._bulb = Bulb(self._ip, auto_on=False)
                self._is_available = True
                p = self._bulb.get_properties()
                self._is_on = True if p["power"] == "on" else False
        except Exception as e:
            # print("lamp not available")
            self._is_available = False

    def _hex_to_rgb(self, hex_string:str) -> dict[str, int]:
        """
        hex_string str : #FFFCCC
        return { "red":(0-255)), "green":(0-255), "blue":(0-255) }
        """
        r_hex = hex_string[1:3]
        g_hex = hex_string[3:5]
        b_hex = hex_string[5:7]
        return {
            "r": int(r_hex, 16),
            "g": int(g_hex, 16),
            "b": int(b_hex, 16),
            "red": int(r_hex, 16),
            "green": int(g_hex, 16),
            "blue": int(b_hex, 16),
        }


    def enable(self) -> None:
        self._is_enabled = True

    def disable(self) -> None:
        self._is_enabled = False

    def turn_off(self) -> None:
        if self._is_available:
            self._bulb.turn_off()
            self._is_on = False

    def turn_on(self) -> None:
        if self._is_available:
            self._bulb.ensure_on()
            self._is_on = True

    def toggle(self) -> None:
        if self._is_available:
            self._bulb.toggle()
            props = self._bulb.get_properties()
            # print("get_properties", props)
            self._is_on = True if props["power"] == "on" else False

    @property
    def is_on(self) -> bool:
        return self._is_on

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value: str) -> None:
        self._color = value
        rgb = self._hex_to_rgb(value)
        if self._is_available:
            # if self._is_on is not True:
            #     self.turn_on()
            self._bulb.set_rgb(rgb["red"], rgb["green"], rgb["blue"])

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, value: int) -> None:
        self._brightness = value
        if self._is_available:
            # if self._is_on:
            self._bulb.set_brightness(value)


if __name__ == "__main__":
    ip = "192.168.15.40"
    print("ip:", ip)
    p = Lampada(enabled=True, ip=ip)
    print("start", p.__dict__)
    print("toggle")
    p.toggle()
    print("final", p.__dict__)
