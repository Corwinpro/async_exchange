from collections import defaultdict
import datetime
from influxdb import InfluxDBClient


INFLUXDB_HOSTNAME = "localhost"
INFLUXDB_PORT = 8086
INFLUXDB_DATABASE = "influxdb_exchange"

TIME_FIELD = "time"
RECORD_TYPE_FIELD = "measurement"
FIELDS_TYPE_FIELD = "fields"

LOG_BATCH_SIZE = 1000


class InfluxDBLogger:
    def __init__(self):
        self.client = InfluxDBClient(
            host=INFLUXDB_HOSTNAME, port=INFLUXDB_PORT
        )
        existing_databases = self.client.get_list_database()

        db_exists = False
        for database in existing_databases:
            if INFLUXDB_DATABASE in database["name"]:
                db_exists = True
                break
        if not db_exists:
            self.client.create_database(INFLUXDB_DATABASE)

        self.client.switch_database(INFLUXDB_DATABASE)

        self._log_batch = defaultdict(list)

    def send_event(self, record_type, message):
        self._log_batch[record_type].append(message)

        if len(self._log_batch[record_type]) >= LOG_BATCH_SIZE:
            self._emit_messages(
                record_type=record_type,
                record_fields=self._log_batch[record_type],
            )
            self._log_batch[record_type] = []

    def _emit_messages(self, record_type, record_fields):
        new_records = [
            {
                TIME_FIELD: datetime.datetime.now().isoformat(),
                RECORD_TYPE_FIELD: record_type,
                FIELDS_TYPE_FIELD: record_field,
            }
            for record_field in record_fields
        ]
        self.client.write_points(new_records)
