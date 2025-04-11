import json
from utils import get_timestamp

class Log:

    def __init__(self):
        self.timestamp = get_timestamp()
        self.records = []

    def __str__(self):
        string = ''
        for record in self.records:
            string += str(record) + '\n'
        return string

    def append_log(self, record):
        self.records.append(record)

    def to_json(self):
        # Serialize list of records as dictionaries
        return {
            "timestamp": self.timestamp,
            "records": [record.to_dict() for record in self.records]
        }


class Record:

    def __init__(self, timestamp, button, is_on_press, coordinates):
        self.timestamp = timestamp  # can be a float or string
        self.button = button
        self.is_on_press = is_on_press
        self.coordinates = coordinates

    def __str__(self):
        # Handle float or string timestamp formatting
        if isinstance(self.timestamp, float):
            timestamp_str = f"{self.timestamp:.6f}"
        else:
            timestamp_str = self.timestamp

        action = 'pressed' if self.is_on_press else 'released'
        coords = f"{int(self.coordinates[0])},{int(self.coordinates[1])}"
        return f"{timestamp_str}    {self.button} {action}    {coords}"

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "button": self.button,
            "is_on_press": self.is_on_press,
            "coordinates": self.coordinates,
        }

