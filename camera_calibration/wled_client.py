import requests
import time


class WLED:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.state_url = f"{self.base_url}/json/state"

    def set_state(self, payload):
        r = requests.post(self.state_url, json=payload, timeout=1)
        r.raise_for_status()

    def all_off(self):
        self.set_state({"on": True, "bri": 0})

    def all_on(self, bri=50):
        self.set_state({"on": True, "bri": bri})

    def set_led_range(self, index_start, index_end, color=(255, 0, 0), bri=128):
        r, g, b = color
        payload = {
            "on": True,
            "bri": bri,
            "seg": [
                {
                    "id": 0,
                    "start": index_start,
                    "stop": index_end,
                    "col": [[r, g, b]],
                }
            ]
        }
        self.set_state(payload)

if __name__ == "__main__":
    w = WLED("http://192.168.0.237")
    w.set_led_range(0, 250, color=(0, 0, 0), bri=0)
    time.sleep(1)

	# Note: "Transitions" should be disabled in the "LED" settings on the WLED HTTP page!
    for i in range(50):
        w.set_led_range(i, i+1, color=(0, 255, 0), bri=20)
        time.sleep(0.1)
        w.set_led_range(i, i+1, color=(0, 0, 0), bri=0)
    
    w.set_led_range(0, 250, color=(0, 0, 0), bri=0)
