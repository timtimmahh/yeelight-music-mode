from flask import Flask, jsonify, render_template, g, request
from Configuration import Configuration, data

app = Flask(__name__, instance_relative_config=True)
config = Configuration()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/devices')
@app.route('/devices/')
def devices():
    g.devices = config.devices
    print(g.devices)
    return render_template('devices.html')


@app.route('/<string:dev>/device', methods=['GET', 'POST'])
@app.route('/<string:dev>/device/', methods=['GET', 'POST'])
def device(dev):
    for device_config in config.devices:
        if device_config.name == dev:
            g.device = device_config
            break
    if request.method == 'POST':
        name = request.form['device_name']
        if name != g.device.data.name or name != g.device.data._capabilities['name']:
            g.device.data.name = name
            g.device.data._capabilities['name'] = name
            g.device.data.set_name(name)
            config.set_device(g.device)

    return render_template('device.html')


@app.route('/schemes')
@app.route('/schemes/')
def schemes():
    return 'Hello'


@app.route('/api/v1', methods=['GET'])
@app.route('/api/v1/', methods=['GET'])
def info_view():
    """
    List of routes for this API.
    """
    output = {
        'info': 'GET /api/v1',
        'devices': 'GET /api/v1/devices',
        'get device': 'GET /api/v1/devices/<device>',
        'edit device': 'PUT /api/v1/devices/<device>',
        'color schemes': 'GET /api/v1/schemes',
        'get color scheme': 'GET /api/v1/schemes/<scheme>',
        'edit color scheme': 'PUT /api/v1/schemes/<scheme>',
        'delete color scheme': 'DELETE /api/v1/schemes/<scheme>'
    }
    return jsonify(output)


@app.route('/api/v1/devices', methods=['GET'])
def get_devices():
    return


@app.route('/api/v1/<string:dev>/device/<string:name>', methods=['POST'])
def set_device(dev, name):
    print(name)
    config.devices.name = name
    return g.device
