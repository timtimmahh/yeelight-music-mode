from flask import Flask, jsonify, render_template, g, request

from Configuration import Configuration

app = Flask(__name__, instance_relative_config=True)
config = Configuration()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/devices', methods=['GET', 'POST'])
@app.route('/devices/', methods=['GET', 'POST'])
def devices(format=None):
    if format == 'json':
        return jsonify({dev.name: dev.data.to_config() for dev in config.devices})
    g.devices = config.devices
    print(g.devices)
    return render_template('devices.html')


@app.route('/<string:dev>/device', methods=['GET', 'POST'])
@app.route('/<string:dev>/device/', methods=['GET', 'POST'])
def device(dev, format=None):
    dev_config = None
    for device_config in config.devices:
        if device_config.name == dev:
            dev_config = device_config
            break
    if request.method == 'POST':
        print(request.form)
        name = request.form['name']
        effect = request.form['effect']
        duration = int(request.form['duration'])
        color_flow = request.form['color_flow']
        should_update = False
        if name != dev_config.data.name or name != dev_config.data.capabilities['name']:
            dev_config.data.name = name
            dev_config.data.capabilities['name'] = name
            dev_config.data.last_properties['name'] = name
            dev_config.data.set_name(name)
            should_update = True
            print('Updating name')
        if effect != dev_config.data.effect:
            dev_config.data.effect = effect
            should_update = True
            print('Updating effect')
        if duration != dev_config.data.duration:
            dev_config.data.duration = duration
            should_update = True
            print('Updating duration')
        if color_flow != dev_config.data.color_flow_mode:
            dev_config.data.color_flow_mode = color_flow
            should_update = True
            print('Updating color flow')

        if should_update:
            config.set_device(dev_config)
    elif format == 'json':
        return jsonify(dev_config.data.to_config())

    g.device = dev_config

    return render_template('device.html')


@app.route('/schemes', methods=['GET', 'POST'])
@app.route('/schemes/', methods=['GET', 'POST'])
def schemes(format=None):
    if format == 'json' and request.method == 'GET':
        return jsonify()
    g.schemes = config.color_schemes

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
