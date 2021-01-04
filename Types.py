from abc import ABC, abstractmethod
from json import dumps

from yeelight import Bulb, PowerMode


class ColorFlow(ABC):

    def __init__(self, name: str, color_ranges=tuple()):
        """
        A music flow configuration.

        :param tuple color_ranges: The color ranges to transition between.
        """
        super().__init__()
        self.name = name
        self.ranges = tuple((cr.start, cr.stop - 1) for cr in color_ranges)

    @property
    @abstractmethod
    def set_bulb_color(self):
        """
        The function used to set the bulb color.
        """
        pass

    def set_color(self, factor: float, bulb: Bulb):
        """
        Set the bulb color based on the audio data factor.
        
        :param float factor: the audio data factor.
        :param Bulb bulb: the bulb to set color.
        """
        self.set_bulb_color(
                bulb,
                *(max_val * factor for (min_val, max_val) in self.ranges)
        )


class RGBColorFlow(ColorFlow):

    def __init__(self,
                 name=None,
                 red_range=range(256),
                 green_range=range(256),
                 blue_range=range(256)):
        """
        An RGB color flow configuration.

        :param tuple red_range: The red range to change between range(0-255).
        :param tuple green_range: The green range to change between range(0-255).
        :param tuple blue_range: The blue range to change between range(0-255).
        """
        if name is None and red_range == range(256) and green_range == range(256) \
                and blue_range == range(256):
            name = f'Default{RGBColorFlow.__name__}'
        super().__init__(name=name, color_ranges=(red_range, green_range, blue_range))

    @property
    def set_bulb_color(self):
        return Bulb.set_rgb

    def __repr__(self) -> str:
        return str(tuple(zip(('red', 'green', 'blue'), self.ranges)))


class HSVColorFlow(ColorFlow):

    def __init__(self,
                 name=None,
                 hue_range=range(400),
                 saturation_range=range(101)):
        """
        An HSV color flow configuration.

        :param tuple hue_range: The hue range to change between range(0-359).
        :param tuple saturation_range: The saturation range to change between range(0-100).
        """
        if name is None and hue_range == range(400) and saturation_range == range(101):
            name = f'Default{HSVColorFlow.__name__}'
        super().__init__(name=name, color_ranges=(hue_range, saturation_range, (100, 100)))

    @property
    def set_bulb_color(self):
        return Bulb.set_hsv

    def __repr__(self) -> str:
        return str(tuple(zip(('hue', 'saturation', 'value'), self.ranges)))


class MusicBulb(Bulb):

    def __init__(self, ip, port=55443, effect="smooth", duration=30, auto_on=False,
                 power_mode=PowerMode.LAST, model=None, dev_id=None, capabilities=None,
                 properties=None,
                 color_flow=RGBColorFlow()):
        """
        The main controller class of a physical YeeLight bulb.

        :param str ip:       The IP of the bulb.
        :param int port:     The port to connect to on the bulb.
        :param str effect:   The type of effect. Can be "smooth" or "sudden".
        :param int duration: The duration of the effect, in milliseconds. The
                             minimum is 30. This is ignored for sudden effects.
        :param bool auto_on: Whether to call :py:meth:`ensure_on()
                             <yeelight.Bulb.ensure_on>` to turn the bulb on
                             automatically before each operation, if it is off.
                             This renews the properties of the bulb before each
                             message, costing you one extra message per command.
                             Turn this off and do your own checking with
                             :py:meth:`get_properties()
                             <yeelight.Bulb.get_properties()>` or run
                             :py:meth:`ensure_on() <yeelight.Bulb.ensure_on>`
                             yourself if you're worried about rate-limiting.
        :param yeelight.PowerMode power_mode:
                             The mode for the light set when powering on.
        :param str model:    The model name of the yeelight (e.g. "color",
                             "mono", etc). The setting is used to enable model
                             specific features (e.g. a particular color
                             temperature range).
        :param str dev_id:  the device's id.
        :param dict capabilities: the device's capabilities. Used for getting
                            capabilities from config file.
        :param dict properties: the device's properties. Used for getting
                             properties from config file.
        :param ColorFlow color_flow: the color flow mode to use for this device.
                             Either RGBColorFlow or HSVColorFlow.
        """
        super().__init__(ip, port, effect, duration, auto_on, power_mode, model)
        if capabilities is None:
            self.get_capabilities()
        else:
            self._capabilities = capabilities
        if properties is None:
            self.get_properties()
        else:
            self._last_properties = properties
        self.dev_id = self.capabilities['id'] if dev_id is None else dev_id
        self.name = self.capabilities['name']
        self.color_flow = color_flow

    @property
    def ip(self):
        """
        Getter for this device's IP address.
        """
        return self._ip

    @property
    def port(self):
        """
        Getter for this device's port.
        """
        return self._port

    @property
    def color_flow_mode(self):
        """
        Getter for this device's color flow mode.
        """
        return 'rgb' if isinstance(self.color_flow, RGBColorFlow) else 'hsv'

    @color_flow_mode.setter
    def color_flow_mode(self, mode):
        """
        Setter for this device's color flow mode.
        """
        self.color_flow = RGBColorFlow() if mode == 'rgb' else HSVColorFlow()

    def set_color(self, factor: float):
        """
        Use the color flow mode to set this device's color from audio data.
        
        :param float factor: The converted audio data to calculate color.
        """
        self.color_flow.set_color(factor, self)

    def __repr__(self):
        return dumps({
            self.dev_id: self.to_config()
        }, indent=2)

    def to_config(self):
        """
        Converts this device to a dictionary in order to save data to config file.
        """
        return dict(
                ip=self.ip,
                port=self.port,
                effect=self.effect,
                duration=self.duration,
                auto_on=self.auto_on,
                power_mode=self.power_mode,
                model=self.model,
                capabilities=self.capabilities,
                properties=self.last_properties,
                color_flow=self.color_flow_mode
        )

    @classmethod
    def from_discovery(cls, data: dict):
        """
        Converts data returned from yeelight.discover_bulbs() into an instance of MusicBulb.

        :param dict data: The data from bulb discover.
        """
        return MusicBulb(
                ip=data['ip'],
                port=data['port'],
                model=data['capabilities']['model'],
                capabilities=data['capabilities']
        )

    @classmethod
    def from_config(cls, dev_id: str, data: dict):
        """
        Converts a dictionary read from a config file into a MusicBulb instance.
        
        :param str dev_id: The device id.
        :param dict data: The config data to use.
        """
        return MusicBulb(
                ip=data['ip'],
                port=data['port'],
                effect=data['effect'],
                duration=data['duration'],
                auto_on=data['auto_on'],
                power_mode=data['power_mode'],
                model=data['model'],
                dev_id=dev_id,
                capabilities=data['capabilities'],
                properties=data['properties'],
                color_flow=HSVColorFlow() if data['color_flow'] == 'hsv' else RGBColorFlow()
        )
