from LightController import Controller
from Configuration import Configuration

if __name__ == '__main__':
    config = Configuration()
    controller = Controller(config)
    controller.start_music()
