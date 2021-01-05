# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from flaskr import config
from flaskr.home import blueprint
from jinja2 import TemplateNotFound

from flask import jsonify, render_template, g, request


@blueprint.route('/index')
def index():
    g.devices = config.devices

    return render_template('index.html')


# @blueprint.route('/devices', methods=['GET', 'POST'])
# @blueprint.route('/devices/', methods=['GET', 'POST'])
# def devices(format=None):
#     if format == 'json':
#         return jsonify({dev.name: dev.data.to_config() for dev in config.devices})
#     g.devices = config.devices
#     print(g.devices)
#     return render_template('devices.html')


@blueprint.route('/<string:dev>/device', methods=['GET'])
@blueprint.route('/<string:dev>/device/', methods=['GET'])
def device(dev, format=None):
    dev_config = None
    for device_config in config.devices:
        if device_config.name == dev:
            dev_config = device_config
            break
    if format == 'json':
        return jsonify(dev_config.data.to_config())

    g.device = dev_config

    return render_template('device.html')


@blueprint.route('/schemes', methods=['GET', 'POST'])
@blueprint.route('/schemes/', methods=['GET', 'POST'])
def schemes(format=None):
    if format == 'json' and request.method == 'GET':
        return jsonify()
    g.schemes = config.color_schemes

    return 'Hello'


@blueprint.route('/api/v1', methods=['GET'])
@blueprint.route('/api/v1/', methods=['GET'])
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


# @blueprint.route('/<template>')
# def route_template(template):
#     try:
#
#         if not template.endswith('.html'):
#             template += '.html'
#
#         # Detect the current page
#         segment = get_segment(request)
#
#         # Serve the file (if exists) from app/templates/FILE.html
#         return render_template(template, segment=segment)
#
#     except TemplateNotFound:
#         return render_template('page-404.html'), 404
#
#     except:
#         return render_template('page-500.html'), 500
#
#
# # Helper - Extract current page name from request
# def get_segment(request):
#     try:
#
#         segment = request.path.split('/')[-1]
#
#         if segment == '':
#             segment = 'index'
#
#         return segment
#
#     except:
#         return None
