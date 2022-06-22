from thttp import request

"""
https://tasmota.github.io/docs/
"""


class Tomada:
    def __init__(self, enabled, ip) -> None:
        self._is_enabled: bool = enabled
        self._is_available: bool = False
        self._is_on: bool = False
        self.ip: str = ip
        self._check_status()

    def _check_status(self) -> bool:
        if not self._is_available:
            resp = self._make_request("cmnd=Power")
            self._is_available = True
            self._is_on = True if resp["POWER"] == "ON" else False
            return self._is_on

    @property
    def is_on(self) -> bool:
        return self._is_on

    def enable(self) -> None:
        self._is_enabled = True

    def disable(self) -> None:
        self._is_enabled = False

    def turn_on(self) -> None:
        if self._is_available:
            r = self._make_request("cmnd=Power%20ON")
            self._is_on = True if r["POWER"] == "ON" else False

    def turn_off(self) -> None:
        if self._is_available:
            r = self._make_request("cmnd=Power%20OFF")
            self._is_on = True if r["POWER"] == "ON" else False

    def toggle(self) -> None:
        if self._is_available:
            r = self._make_request(f"cmnd=Power%20TOGGLE")
            self._is_on = True if r["POWER"] == "ON" else False

    def _make_request(self, query_string: str):
        try:
            r = request(f"http://{self.ip}/cm?{query_string}", timeout=1, verify=False)
            if r.status == 200:
                return r.json
        except Exception as e:
            self._is_available = False
        return None
