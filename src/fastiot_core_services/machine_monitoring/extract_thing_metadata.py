from datetime import datetime
from typing import List

from fastiot.msg.thing import Thing
from fastiot.util.csv_reader import CSVReader


def extract_thing_metadata_from_csv(file: str) -> List[Thing]:
    result: List[Thing] = []
    with CSVReader(file,
                   required_fields=['machine', 'name'],
                   optional_fields=['unit']
                   ) as reader:
        for row in reader:
            thing = Thing(
                machine=str(row['machine']),
                name=str(row['name']),
                unit=str(row.get('unit', '')),
                value=None,
                timestamp=datetime.min
            )
            result.append(thing)
    return result
