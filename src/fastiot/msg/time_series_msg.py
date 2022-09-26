from datetime import datetime
from typing import Any, Dict

from fastiot.core.data_models import FastIoTData


class TimeSeriesData(FastIoTData):
    id: str
    name: str
    service_id: str
    measurement_id: str
    dt_start: datetime
    dt_end: datetime
    modified_at: datetime
    values: Any

    def to_dict(self) -> Dict:
        time_series_dict = self.dict()
        return time_series_dict

    @staticmethod
    def from_dict(dict: Dict) -> 'TimeSeriesData':
        time_series_data = TimeSeriesData.parse_obj(dict)
        return time_series_data

