import asyncio

from async_exchange.api import Exchange
from async_exchange.algorithms.random_trader import RandomTrader
from async_exchange.logging.influxdb_logger import InfluxDBLogger


NOF_TRADERS = 100


async def main():
    exchange = Exchange(logger=InfluxDBLogger())
    api = exchange.api
    tasks = [
        RandomTrader(exchange_api=api, money=300, stocks=10).cycle()
        for _ in range(NOF_TRADERS)
    ]
    group = asyncio.gather(*tasks, return_exceptions=False)
    await group


if __name__ == "__main__":
    asyncio.run(main())
