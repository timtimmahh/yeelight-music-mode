from Configuration import Configuration
from LightController import Controller

if __name__ == '__main__':
    config = Configuration()
    controller = Controller(config)
    controller.start_music()
