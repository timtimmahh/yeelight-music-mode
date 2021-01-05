from flaskr import config
from flask import jsonify, render_template, g, request
from flaskr.home import blueprint


def parse_post_data(device, form):
    def update_name(name):
        if name != device.data.name or name != device.data.capabilities['name']:
            device.data.name = name
            device.data.capabilities['name'] = name
            device.data.last_properties['name'] = name
            device.data.set_name(name)
            return True
        return False

    def update_effect(effect):
        if effect != device.data.effect:
            device.data.effect = effect
            return True
        return False

    def update_duration(duration):
        if duration != device.data.duration:
            device.data.duration = duration
            return True
        return False

    def update_color_flow(color_flow):
        if color_flow != device.data.color_flow_mode:
            device.data.color_flow_mode = color_flow
            return True
        return False

    data = dict(
        name=update_name,
        effect=update_effect,
        duration=update_duration,
        color_flow=update_color_flow
    )

    should_update = False
    for arg, func in data:
        should_update = arg in form and func(form[arg])

    if should_update:
        config.set_device(device)


@blueprint.route('/device/<string:device>/', methods=['GET', 'POST'])
@blueprint.route('/device/<string:device>', methods=['GET', 'POST'])
def device_update(device, **post_data):
    if request.method == 'POST':
        parse_post_data(config.devices[device], **post_data)


@blueprint.route('/device/<string:dev_id>/toggle')
def toggle(dev_id):
    device = config.devices[dev_id]
    state = device.capabilities['power']
    if device.toggle() == 'ok':
        device.capabilities['power'] = 'off' if state == 'on' else 'on'
    return jsonify(original_state=state, new_state=device.capabilities['power'])
