# Async_exchange

`async_exchange` is lightweight python library for concurrent multi-agent stock exchange simulation.

`async_exchange` is designed in way that the simulations can be run in a single thread, and the agents can interact with the exchange in a asynchronous way.

## Quickstart

The basic usage of the `async_exchange` does not require any additional dependencies.
Install the package in your preferred environment, and try the [demo](demos/run_exchange.py).

Create your own trader agents in two steps:

1. Define a subclass of the [`Trader`](async_exchange/trader.py) that implements an asynchronous  `cycle()` method.
  The `cycle` method should emulate the agent's thinking and decision making process.
  The agent can get information about the existing order book, own standing orders via the `exchange_api` methods.

    In the demo example, the `cycle` consists of a "sleep" phase (the agent is inactive) and a random order submission.

    ```python
    class RandomTrader(Trader):
        async def cycle(self):
            while True:
                await self.sleep()
                self.place_random_order()
    ```
  
    Note that if any actual CPU-bound computations happen inside the `cycle` method of an agent, the whole event loop will be blocked.
    Consider delegating heavy computations to an external process that can be awaited.

2. Create an environment of agents (not necessarily of the same type), and run the simulation.

    Users are welcome to implement their own post-processing and analysis tools.
    In the following sections, we introduce a possible way to store logs and visualize the trading history.

### Logging

Users can implement their own logger and pass it to the `Exchange` instance.
The logger must implement a `send_event` method with two arguments: an `event_type` string, and a `message`.

#### InfluxDB logging

There exists a built-in logging infrastructure.

The [`InfluxDBLogger`](async_exchange/logging/influxdb_logger.py) stores the information about all successful exchange operations from the [`Exchange`](async_exchange/exchange.py) to a local InfluxDB.

First, install necessary `influxdb` requirements from the `setup/influxdb/requirements.txt`.

Second, the logger expects an InfluxDB service available on `http://localhost:8086` with a database called `influxdb_exchange`.
It is suggested that the [docker-compose.yml](setup/influxdb/docker-compose.yml) file is used to spin required services via docker.
*Important*: the `docker-compose` expect that the `/tmp/exchange/influxdb`  directory exists on the host machine.
```sh
$ cd setup/influxdb
$ docker-compose -f docker-compose.yml up -d
```

### Visualization

If the `docker-compose` method from the previous section was used to set up logging, a Grafana service is a suggested way to visualize trading sessions.

1. Login to Grafana at `http://localhost:3031` using the standard `admin`/`admin` username and password.
2. A visualization dashboard should already be created.
   Start the trading experiment, and the candlestick chart should appear shortly (the dashboard updates every 10 seconds).
