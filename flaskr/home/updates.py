from flaskr import config
from flask import jsonify, render_template, g, request
from flaskr.home import blueprint


def get_device(device):



def update_name(device, name):
    if name != dev_config.data.name or name != dev_config.data.capabilities['name']:
        dev_config.data.name = name
        dev_config.data.capabilities['name'] = name
        dev_config.data.last_properties['name'] = name
        dev_config.data.set_name(name)



def parse_post_data(**data):



@blueprint.route('/device/<string:device>/', methods=['GET', 'POST'])
@blueprint.route('/device/<string:device>', methods=['GET', 'POST'])
def device_update(device):



if request.method == 'POST':
    print(request.form)
    name = request.form['name']
    effect = request.form['effect']
    duration = int(request.form['duration'])
    color_flow = request.form['color_flow']
    should_update = False
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