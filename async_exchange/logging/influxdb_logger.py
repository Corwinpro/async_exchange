from collections import defaultdict
import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


INFLUXDB_HOSTNAME = "localhost"
INFLUXDB_ORG = "async_exchange_org"
INFLUXDB_BUCKET_NAME = "async_exchange_bucket"
INFLUXDB_PORT = 8086
INFLUXDB_URL = (
    f"http://{INFLUXDB_HOSTNAME}:{INFLUXDB_PORT}"
)
INFLUXDB_TOKEN = "async_exchange_token"
headers = {}
headers["Authorization"] = f"Token {INFLUXDB_TOKEN}"
INFLUXDB_DATABASE = "influxdb_exchange"

TIME_FIELD = "time"
RECORD_TYPE_FIELD = "measurement"
FIELDS_TYPE_FIELD = "fields"

LOG_BATCH_SIZE = 10


class InfluxDBLogger:
    def __init__(self):
        self.client = InfluxDBClient(
            url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

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
            Point.from_dict(
                {
                    TIME_FIELD: datetime.datetime.now().isoformat(),
                    RECORD_TYPE_FIELD: record_type,
                    FIELDS_TYPE_FIELD: record_field,
                }
            )
            for record_field in record_fields
        ]
        self.write_api.write(bucket=INFLUXDB_BUCKET_NAME, record=new_records)
