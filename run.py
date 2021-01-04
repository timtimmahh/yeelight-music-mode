from flaskr import app
from LightController import Controller
from Configuration import Configuration

if __name__ == '__main__':
    app.run(debug=True)
    config = Configuration()
    controller = Controller(config)
    controller.start_music()
