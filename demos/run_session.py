from async_exchange.algorithms.random_trader import RandomTrader
from async_exchange.trading_session import TradingSession

try:
    from async_exchange.logging.influxdb_logger import InfluxDBLogger
except ImportError:
    logger = None
    RandomTrader.verbose = True
else:
    logger = InfluxDBLogger()
    RandomTrader.verbose = False


NOF_TRADERS = 100


if __name__ == "__main__":

    traders = [RandomTrader(money=300, stocks=10) for _ in range(NOF_TRADERS)]
    session = TradingSession(traders=traders, logger=logger)
    session.run()
