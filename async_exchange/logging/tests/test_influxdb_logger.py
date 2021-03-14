import unittest

from async_exchange.logging.influxdb_logger import InfluxDBLogger


class TestInfluxDBLogger(unittest.TestCase):
    def setUp(self):
        self.logger = InfluxDBLogger(database_name="test_db", batch_size=1)
        self.addCleanup(self.logger.client.close)
        self.addCleanup(self.logger.client.drop_database, "test_db")

    def test__emit_messages(self):
        self.logger._emit_messages(
            record_type="my_event_type",
            record_fields=[{"data": 1, "comment": "another comment"}],
        )

        (point,) = self.logger.get_points("my_event_type")
        self.assertEqual(point["data"], 1)
        self.assertEqual(point["comment"], "another comment")

    def test_send_event_in_batches_one(self):
        self.assertEqual(self.logger.batch_size, 1)

        self.logger.send_event(record_type="type", message={"data": "my data"})
        (point,) = self.logger.get_points("type")
        self.assertEqual(point["data"], "my data")

    def test_send_event_in_batches_many(self):
        self.logger.batch_size = 10
        self.assertEqual(self.logger.batch_size, 10)

        for i in range(9):
            self.logger.send_event(
                record_type="type", message={"data": f"my data {i}"}
            )

        points = list(self.logger.get_points("type"))
        self.assertEqual(len(points), 0)

        self.logger.send_event(
            record_type="type", message={"data": "my data 9"}
        )
        for i, point in enumerate(self.logger.get_points("type")):
            self.assertEqual(point["data"], f"my data {i}")

        self.assertEqual(len(self.logger._log_batch["type"]), 0)


if __name__ == "__main__":
    unittest.main()
