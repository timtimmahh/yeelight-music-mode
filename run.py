from decouple import config
from config import config_dict
from flaskr import create_app

DEBUG = config('DEBUG', default=True)

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

app_config = config_dict[get_config_mode.capitalize()]

app = create_app(app_config)

if __name__ == '__main__':
    app.run()
