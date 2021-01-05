from abc import ABC, abstractmethod
from json import dump, load
from os.path import exists

from yeelight import discover_bulbs as discover

from .Types import MusicBulb, ColorFlow


def read_config():
    """
    Read JSON data from the config file.
    """
    if exists('../config.json'):
        with open('../config.json') as cfg:
            d = load(cfg)
    else:
        d = dict()
        global no_configs
        no_configs = True

    if 'devices' not in d:
        d['devices'] = dict()

    if 'schemes' not in d:
        d['schemes'] = dict()

    return d


def save_config():
    """
    Save JSON data to the config file.
    """
    with open('../config.json', 'w') as cfg:
        dump(data, cfg, indent=2)


no_configs = False
data = read_config()


def discover_bulbs():
    """
    Discover all bulbs on the network and create MusicBulb instances.
    """
    return [MusicBulb.from_discovery(d) for d in discover()]


class Configuration:

    def __init__(self) -> None:
        """
        Manages the program configuration data.
        """
        super().__init__()
        self._devices = DeviceConfig.get_all()
        self._color_schemes = SchemeConfig.get_all()
        if no_configs:
            self.perform_discovery()

    def add_device(self, device):
        """
        Add a new device to the configuration data.

        :param MusicBulb device: The new device to add.
        """
        self._devices += [DeviceConfig.save(device)]

    def set_device(self, device):
        """
        Updates an existing device in the configuration data.

        :param DeviceConfig device: The device config to update.
        """
        for i in range(len(self.devices)):
            if self.devices[i].name == device.name:
                self.devices[i] = device
                data['devices'][device.name] = device.data.to_config()
                save_config()
                break

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

    def perform_discovery(self):
        """
        Performs bulb discovery for the configuration instance
        if data is missing from the config file.
        """
        bulbs = discover_bulbs()
        ids = [device.name for device in self.devices]
        for bulb in bulbs:
            if bulb.dev_id not in ids:
                self.add_device(bulb)


class Config(ABC):

    @staticmethod
    @abstractmethod
    def get_all():
        pass

    def __init__(self, name: str, cls, **kwargs) -> None:
        """
        A configuration for specific data.
        
        :param str name: The name of the config data.
        :param Any cls: The class to wrap with configurations.
        :param kwargs: Any additional data for the wrapped data type.
        """
        super().__init__()
        self.name = name
        if 'device' not in kwargs:
            self._data = cls(**kwargs)
        else:
            self._data = kwargs['device']

    @property
    def data(self):
        """
        Getter for the wrapped data type.
        """
        return self._data


class DeviceConfig(Config):

    @staticmethod
    def get_all():
        """
        Gets all DeviceConfig data from the config file.
        """
        return [DeviceConfig(dev_id, device=MusicBulb.from_config(dev_id, device))
                for dev_id, device in data['devices'].items()]

    @staticmethod
    def save(device: MusicBulb):
        """
        Save a MusicBulb instance to the config file.
        """
        data['devices'][device.dev_id] = device.to_config()
        save_config()
        return DeviceConfig(device.dev_id, device=device)

    def __init__(self, dev_id: str, **kwargs) -> None:
        super().__init__(
            dev_id,
            MusicBulb,
            **kwargs
        )


class SchemeConfig(Config):

    @staticmethod
    def get_all():
        """
        Gets all SchemeConfig data from the config file.
        """
        return [SchemeConfig(cs_id, **scheme) for cs_id, scheme in data['schemes'].items()]

    @staticmethod
    def save(device):
        pass
        # section = {
        # 
        # }
        # data['devices'][device['capabilities']['id']] = section
        # save_config()
        # return SchemeConfig(device['capabilities']['id'], **section)

    def __init__(self, name, **kwargs) -> None:
        super().__init__(
            name,
            ColorFlow,
            **kwargs
        )
