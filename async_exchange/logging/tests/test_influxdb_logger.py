import unittest

from async_exchange.logging.influxdb_logger import InfluxDBLogger


class TestInfluxDBLogger(unittest.TestCase):
    def setUp(self):
        self.logger = InfluxDBLogger(database_name="test_db")
        self.addCleanup(self.logger.client.close)
        self.addCleanup(self.logger.client.drop_database, "test_db")

    def test_send_message(self):
        self.logger._emit_messages(
            record_type="my_event_type",
            record_fields=[{"data": 1, "comment": "another comment"}]
        )

        client = self.logger.client
        measurements = client.get_list_measurements()
        self.assertEqual(measurements, [{'name': 'my_event_type'}])

        data = client.query("select * from my_event_type;")
        point, = data.get_points()
        self.assertEqual(point["data"], 1)
        self.assertEqual(point["comment"], "another comment")


if __name__ == "__main__":
    unittest.main()
