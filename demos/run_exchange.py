import asyncio

from async_exchange.api import Exchange
from async_exchange.algorithms.random_trader import RandomTrader


NOF_TRADERS = 100


async def main():
    exchange = Exchange()
    api = exchange.api
    tasks = [
        RandomTrader(exchange_api=api, money=300, stocks=10).cycle()
        for _ in range(NOF_TRADERS)
    ]
    group = asyncio.gather(*tasks, return_exceptions=True)
    await group


if __name__ == "__main__":
    asyncio.run(main())
