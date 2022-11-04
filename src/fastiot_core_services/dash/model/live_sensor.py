import datetime


class LiveSensor:
    def __init__(self, name, machine, customer, module):
        self.live_sensors = []
        self.name = name
        self.machine = machine
        self.customer = customer
        self.module = module

    def clean_until(self, current_time, max_delta):
        try:
            while self.live_sensors[0].timestamp < current_time - datetime.timedelta(0, max_delta):
                self.live_sensors.pop(0)
        except IndexError:
            pass
