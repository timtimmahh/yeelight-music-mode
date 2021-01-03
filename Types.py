from yeelight import Bulb, PowerMode
from json import dumps
from abc import ABC, abstractmethod
import numpy as np


class ColorFlow(ABC):

    def __init__(self, name: str, color_ranges=tuple()):
        """
        A music flow configuration.

        :param tuple color_ranges: The color ranges to transition between.
        """
        super().__init__()
        self.name = name
        self.ranges = color_ranges

    @property
    @abstractmethod
    def set_bulb_color(self):
        pass

    def set_color(self, factor: float, bulb: Bulb):
        # print(f'factor={factor} rgb={type(factor * 128.0 * 2)} -'
        #       f' {[]}')
        self.set_bulb_color(
            bulb,
            *((len(i) - 1) * factor for i in self.ranges)
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
        # self.set_color_func = lambda bulb: bulb.set_rgb

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
        super().__init__(name=name, color_ranges=(hue_range, saturation_range, (100,)))

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
        return self._ip

    @property
    def port(self):
        return self._port

    def set_color(self, factor: float):
        self.color_flow.set_color(factor, self)

    def __repr__(self):
        return dumps({
            self.dev_id: self.to_config()
        }, indent=2)

    def to_config(self):
        return dict(
            ip=self.ip,
            port=self.port,
            effect=self.effect,
            duration=self.duration,
            auto_on=self.auto_on,
            power_mode=self.power_mode,
            model=self.model,
            capabilities=self.capabilities,
            properties=self.last_properties
        )

    @classmethod
    def from_discovery(cls, data: dict):
        return MusicBulb(
            ip=data['ip'],
            port=data['port'],
            model=data['capabilities']['model'],
            capabilities=data['capabilities']
        )

    @classmethod
    def from_config(cls, dev_id: str, data: dict):
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
            properties=data['properties']
        )
