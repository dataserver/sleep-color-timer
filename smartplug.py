import requests

"""
https://tasmota.github.io/docs/F
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
            self._is_on = True if resp["POWER"]=="ON" else False
            return self._is_on

    @property
    def is_on(self):
        return self._is_on

    def enable(self):
        self._is_enabled = True

    def disable(self):
        self._is_enabled = False

    def turn_on(self) -> None:
        if self._is_available:
            r = self._make_request("cmnd=Power%20ON")
            self._is_on = True if r["POWER"]=="ON" else False

    def turn_off(self) -> None:
        if self._is_available:
            r = self._make_request("cmnd=Power%20OFF")
            self._is_on = True if r["POWER"]=="ON" else False

    def toggle(self) -> None:
        if self._is_available:
            r = self._make_request(f"cmnd=Power%20TOGGLE")
            self._is_on = True if r["POWER"]=="ON" else False

    def _make_request(self, query_string:str) -> dict[str, object]:
        try :
            r = requests.get(f"http://{self.ip}/cm?{query_string}", timeout=1)
            if r.status_code == 200:
                return r.json()
        except requests.exceptions.JSONDecodeError:
            print('response is not json')
            self._is_available  = False
        except requests.exceptions.Timeout:
            print('response time out')
            self._is_available  = False
        return None





if __name__ == "__main__":
    ip = "192.168.15.41"
    print("ip:", ip)
    p = Tomada(enabled=True, ip=ip)
    print("start", p.__dict__)
    print("toggle")
    p.toggle()
    print("final", p.__dict__)
