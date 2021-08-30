import logging

from influxdb_client import (
    BucketRetentionRules,
    InfluxDBClient,
    Point,
    WriteOptions
)


logger = logging.getLogger(__name__)

INFLUXDB_HOSTNAME = "http://localhost"
INFLUXDB_PORT = 8086
INFLUXDB_URL = f"{INFLUXDB_HOSTNAME}:{INFLUXDB_PORT}"

# A default auth token
INFLUXDB_TOKEN = "my-super-secret-auth-token"
ORGANIZATION = "myorg"
BUCKET = "exchange"

TIME_FIELD = "time"
RECORD_TYPE_FIELD = "measurement"
FIELDS_TYPE_FIELD = "fields"

LOG_BATCH_SIZE = 1000


class InfluxDBLogger:
    def __init__(
        self,
        bucket_name=BUCKET,
        batch_size=LOG_BATCH_SIZE,
        data_retention=3600,
    ):
        self.organization = ORGANIZATION
        self.client = InfluxDBClient(
            url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=self.organization
        )
        self.batch_size = batch_size
        self.bucket_name = bucket_name

        self.write_api = self.client.write_api(
            write_options=WriteOptions(batch_size=self.batch_size)
        )
        self.query_api = self.client.query_api()
        self.buckets_api = self.client.buckets_api()
        bucket = self.buckets_api.find_bucket_by_name(self.bucket_name)
        if bucket is None:
            logger.warning(
                f"Bucket {self.bucket_name!r} not found. "
                f"Creating a bucket {self.bucket_name!r}."
            )
            retention_rules = None
            if data_retention is not None:
                retention_rules = BucketRetentionRules(
                    type="expire", every_seconds=data_retention
                )
            self.buckets_api.create_bucket(
                bucket_name=self.bucket_name,
                retention_rules=retention_rules,
                org=self.organization,
            )

    def send_event(self, record_type, message):
        point = Point(record_type)
        for key, value in message.items():
            point = point.field(key, value)
        self.write_api.write(bucket=self.bucket_name, record=point)

    def get_events(self, record_type):
        query = '''
            from(bucket: currentBucket)
            |> range(start: -5m, stop: now())
            |> filter(fn: (r) => r._measurement == recordType)
            |> pivot(rowKey:["_time"], columnKey: ["_field"], \
                valueColumn: "_value")
        '''
        params = {"currentBucket": self.bucket_name, "recordType": record_type}
        tables = self.query_api.query(query=query, params=params)
        if len(tables) > 0:
            table, *_ = tables
            events = table.records
        else:
            events = []
        return events
