import unittest

from influxdb_client.client.write_api import SYNCHRONOUS

from async_exchange.logging.influxdb_logger import InfluxDBLogger


class TestInfluxDBLogger(unittest.TestCase):
    def setUp(self):
        self.logger = InfluxDBLogger(bucket_name="test_bucket", batch_size=10)

        def cleanup_bucket():
            bucket = self.logger.buckets_api.find_bucket_by_name("test_bucket")
            self.logger.buckets_api.delete_bucket(bucket=bucket)

        self.addCleanup(cleanup_bucket)
        self.addCleanup(self.logger.client.close)

    def test_send_event_get_event(self):
        # Convert the write API to synchronous to avoid waiting for background
        # threads finishing writing
        self.logger.write_api = self.logger.client.write_api(
            write_options=SYNCHRONOUS
        )

        self.logger.send_event(
            record_type="type",
            message={"data": "my data", "another data": "something else"}
        )
        point, = self.logger.get_events("type")
        self.assertEqual(point["_measurement"], "type")
        self.assertEqual(point["data"], "my data")
        self.assertEqual(point["another data"], "something else")

    def test_batch_set(self):
        self.assertEqual(
            self.logger.write_api._write_options.batch_size, 10
        )


if __name__ == "__main__":
    unittest.main()
