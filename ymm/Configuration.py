from json import dump, load
from os.path import exists

from yeelight import discover_bulbs as discover

from .Types import MusicBulb, ColorFlow, RGBColorFlow, HSVColorFlow


def discover_bulbs():
    """
    Discover all bulbs on the network and create MusicBulb instances.
    """
    return [MusicBulb.from_discovery(d) for d in discover()]


def read_config():
    """
    Read JSON data from the config file.
    """
    if exists('../config.json'):
        with open('../config.json') as cfg:
            d = load(cfg)
    else:
        d = dict()

    if 'devices' not in d:
        d['devices'] = dict()

    if 'schemes' not in d:
        d['schemes'] = dict()

    def cls(scheme: dict):
        return RGBColorFlow if scheme['ft'] == 'rgb' else HSVColorFlow

    return (
        {dev_id: MusicBulb.from_config(dev_id, device) for dev_id, device in d['devices'].items()},
        {cs_id: cls(scheme).from_config(cs_id, scheme) for cs_id, scheme in d['schemes'].items()}
    )


class Configuration:

    def _save_config(self):
        """
        Save JSON data to the config file.
        """
        with open('../config.json', 'w') as cfg:
            dump(self.as_config, cfg, indent=2)

    def __init__(self) -> None:
        """
        Manages the program configuration data.
        """
        super().__init__()

        self._devices, self._color_schemes = read_config()
        if len(self._devices) == 0:
            self.update_devices(discover_bulbs())

    def update_device(self, device):
        self.devices[device.dev_id] = device
        self._save_config()

    def update_devices(self, devices):
        for device in devices:
            self.devices[device.dev_id] = device
        self._save_config()

    @property
    def devices(self):
        """
        Getter for configured devices.
        """
        return self._devices

    @property
    def color_schemes(self):
        """
        Getter for configured color schemes.
        """
        return self._color_schemes

    @property
    def as_config(self):
        return dict(
            devices={dev_id: device.to_config() for dev_id, device in self.devices.items()},
            schemes={cs_id: scheme.to_config() for cs_id, scheme in self.color_schemes.items()}
        )

# class Config(ABC):
#
#     @staticmethod
#     @abstractmethod
#     def get_all(dict_data: dict):
#         pass
#
#     def __init__(self, name: str, cls, **kwargs) -> None:
#         """
#         A configuration for specific data.
#
#         :param str name: The name of the config data.
#         :param Any cls: The class to wrap with configurations.
#         :param kwargs: Any additional data for the wrapped data type.
#         """
#         super().__init__()
#         self.name = name
#         if 'device' not in kwargs:
#             self._data = cls(**kwargs)
#         else:
#             self._data = kwargs['device']
#
#     @property
#     def data(self):
#         """
#         Getter for the wrapped data type.
#         """
#         return self._data
#
#
# class DeviceConfig(Config):
#
#     @staticmethod
#     def get_all(dict_data: dict):
#         """
#         Gets all DeviceConfig data from the config file.
#         """
#         return {dev_id: DeviceConfig(dev_id, device=MusicBulb.from_config(dev_id, device))
#                 for dev_id, device in dict_data.items()}
#
#     @staticmethod
#     def save(device: MusicBulb):
#         """
#         Save a MusicBulb instance to the config file.
#         """
#         data['devices'][device.dev_id] = device.to_config()
#         save_config()
#         return DeviceConfig(device.dev_id, device=device)
#
#     def __init__(self, dev_id: str, **kwargs) -> None:
#         super().__init__(
#             dev_id,
#             MusicBulb,
#             **kwargs
#         )
#
#
# class SchemeConfig(Config):
#
#     @staticmethod
#     def get_all(dict_data: dict):
#         """
#         Gets all SchemeConfig data from the config file.
#         """
#         return {cs_id: SchemeConfig(cs_id, **scheme) for cs_id, scheme in dict_data.items()}
#
#     @staticmethod
#     def save(device):
#         pass
#         # section = {
#         #
#         # }
#         # data['devices'][device['capabilities']['id']] = section
#         # save_config()
#         # return SchemeConfig(device['capabilities']['id'], **section)
#
#     def __init__(self, name, **kwargs) -> None:
#         super().__init__(
#             name,
#             ColorFlow,
#             **kwargs
#         )
