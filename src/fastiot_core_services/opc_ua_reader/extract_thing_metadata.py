from datetime import datetime
from typing import Dict

from fastiot.msg.thing import Thing
from fastiot.util.csv_reader import CSVReader


def extract_thing_metadata_from_csv(file: str) -> Dict[str, Thing]:
    result: Dict[str, Thing] = {}
    with CSVReader(file,
                   required_fields=['nodeid', 'machine', 'thing_name'],
                   optional_fields=['unit']
                   ) as reader:
        for row in reader:
            thing = Thing(
                machine=str(row['machine']),
                name=str(row['thing_name']),
                unit=str(row.get('unit', '')),
                value=None,
                timestamp=datetime.min
            )
            result[row['nodeid']] = thing
    return result
