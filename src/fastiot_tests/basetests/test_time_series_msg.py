import unittest
from datetime import datetime

from fastiot.msg.time_series_msg import TimeSeriesData

time_series_data = TimeSeriesData(
    id='12345',
    name='machine1.sensor1',
    service_id='12345',
    measurement_id='12345',
    dt_start=datetime(year=2022, month=9, day=1, second=1),
    dt_end=datetime(year=2022, month=9, day=1, second=3),
    modified_at=datetime(year=2022, month=9, day=1, second=3),
    values=[10, 11, 12])


class TestTimeSeriesData(unittest.TestCase):

    def test_to_and_from_dict(self):
        time_series_data_dict = time_series_data.to_dict()
        time_series_data_converted = TimeSeriesData.from_dict(time_series_data_dict)
        self.assertEqual(time_series_data, time_series_data_converted)
