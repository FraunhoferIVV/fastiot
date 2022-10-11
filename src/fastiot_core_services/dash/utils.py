""" This class holds some tools to work with Flask within SAM modules covering async and threading.

As of know it seems to be working but it is only lightly tested. Please use with caution!
"""
import threading

from werkzeug.serving import make_server

from fastiot_core_services.dash.env import env_dash


class ServerThread(threading.Thread):

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.srv = make_server('0.0.0.0', env_dash.dash_port, app, threaded=True)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()
