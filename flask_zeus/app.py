# encoding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from flask import Flask


def create_app(config, config_name='default', ext_list=None, bp_list=None, **kwargs):
    app = Flask(__name__, **kwargs)
    app_config = config.get(config_name)
    app.config.from_object(app_config)

    if hasattr(app_config, 'init_app'):
        app_config.init_app(app)

    if ext_list and isinstance(ext_list, (list, tuple, set)):
        for ext in ext_list:
            ext.init_app(app)

    if bp_list and isinstance(bp_list, (list, tuple, set)):
        for bp in bp_list:
            app.register_blueprint(bp)

    return app
