# import configparser
from json import dump, load
from yeelight import discover_bulbs as discover
from Types import MusicBulb, ColorFlow
import yeelight.flows
from os.path import exists


# parser = configparser.ConfigParser()
# with open('config.ini') as cfg:
#     parser.read_file(cfg)


def read_config():
    if exists('config.json'):
        with open('config.json') as cfg:
            d = load(cfg)
    else:
        d = dict()

    if 'devices' not in d:
        d['devices'] = dict()

    if 'schemes' not in d:
        d['schemes'] = dict()

    return d


def save_config():
    with open('config.json', 'w') as cfg:
        dump(data, cfg, indent=2)


data = read_config()


def discover_bulbs():
    return [MusicBulb.from_discovery(d) for d in discover()]


class Configuration:

    def __init__(self) -> None:
        super().__init__()
        self._devices = DeviceConfig.get_all()
        self._color_schemes = SchemeConfig.get_all()

    def add_device(self, device):
        self._devices += [DeviceConfig.save(device)]
        
    def set_device(self, device):
        for i in range(len(self.devices)):
            if self.devices[i].name == device.dev_id:
                self.devices[i] = device

    @property
    def devices(self):
        return self._devices

    @property
    def color_schemes(self):
        return self._color_schemes


class Config(object):

    @staticmethod
    def get_all():
        pass

    def __init__(self, name: str, cls, **kwargs) -> None:
        super().__init__()
        self.name = name
        if 'device' not in kwargs:
            self._data = cls(**kwargs)
        else:
            self._data = kwargs['device']

    @property
    def data(self):
        return self._data


class DeviceConfig(Config):

    @staticmethod
    def get_all():
        return [DeviceConfig(dev_id, device=MusicBulb.from_config(dev_id, device))
                for dev_id, device in data['devices'].items()]

    @staticmethod
    def save(device: MusicBulb):
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
