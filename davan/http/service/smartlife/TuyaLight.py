#from davan.http.service.smartlife.TuyaDevice import TuyaDevice
import davan.http.service.smartlife.TuyaUtil as TuyaUtil

class TuyaDevice:
    def __init__(self, data, session):
        self.session = session
        self.data = data.get("data")
        self.obj_id = data.get("id")
        self.obj_type = data.get("ha_type")
        self.obj_name = data.get("name")
        self.dev_type = data.get("dev_type")
        self.icon = data.get("icon")

    def name(self):
        return self.obj_name

    def state(self):
        state = self.data.get("state")
        if state == "true":
            return True
        else:
            return False

    def device_type(self):
        return self.dev_type

    def object_id(self):
        return self.obj_id

    def object_type(self):
        return self.obj_type

    def available(self):
        return self.data.get("online")

    def iconurl(self):
        return self.icon

    def update(self):
        """Avoid get cache value after control."""
        time.sleep(0.5)
        success, response = TuyaUtil.device_control(
            self.session, self.obj_id, "QueryDevice", namespace="query"
        )
        if success:
            self.data = response["payload"]["data"]
            return True
        return
class TuyaLight(TuyaDevice):
    def state(self):
        state = self.data.get("state")
        if state == "true":
            return True
        else:
            return False

    def brightness(self):
        work_mode = self.data.get("color_mode")
        if work_mode == "colour" and "color" in self.data:
            brightness = int(self.data.get("color").get("brightness") * 255 / 100)
        else:
            brightness = self.data.get("brightness")
        return brightness

    def _set_brightness(self, brightness):
        work_mode = self.data.get("color_mode")
        if work_mode == "colour":
            self.data["color"]["brightness"] = brightness
        else:
            self.data["brightness"] = brightness

    def support_color(self):
        if self.data.get("color") is None:
            return False
        else:
            return True

    def support_color_temp(self):
        if self.data.get("color_temp") is None:
            return False
        else:
            return True

    def hs_color(self):
        if self.data.get("color") is None:
            return None
        else:
            work_mode = self.data.get("color_mode")
            if work_mode == "colour":
                color = self.data.get("color")
                return color.get("hue"), color.get("saturation")
            else:
                return 0.0, 0.0

    def color_temp(self):
        if self.data.get("color_temp") is None:
            return None
        else:
            return self.data.get("color_temp")

    def min_color_temp(self):
        return 10000

    def max_color_temp(self):
        return 1000

    def turn_on(self):
        TuyaUtil.device_control(self.session, self.obj_id, "turnOnOff", {"value": "1"})

    def turn_off(self):
        TuyaUtil.device_control(self.session, self.obj_id, "turnOnOff", {"value": "0"})

    def set_brightness(self, brightness):
        """Set the brightness(0-255) of light."""
        value = int(brightness * 100 / 255)
        TuyaUtil.device_control(self.session, self.obj_id, "brightnessSet", {"value": value})

    def set_color(self, color):
        """Set the color of light."""
        hsv_color = {}
        hsv_color["hue"] = color[0]
        hsv_color["saturation"] = color[1] / 100
        if len(color) < 3:
            hsv_color["brightness"] = int(self.brightness()) / 255.0
        else:
            hsv_color["brightness"] = color[2]
        # color white
        if hsv_color["saturation"] == 0:
            hsv_color["hue"] = 0
        TuyaUtil.device_control(self.session, self.obj_id, "colorSet", {"color": hsv_color})

    def set_color_temp(self, color_temp):
        TuyaUtil.device_control(
            self.session, self.obj_id, "colorTemperatureSet", {"value": color_temp}
        )