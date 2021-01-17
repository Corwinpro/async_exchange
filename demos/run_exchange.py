from async_exchange.api import Exchange, Trader

if __name__ == "__main__":

    exchange = Exchange()

    trader_1 = Trader(exchange=exchange)
    trader_2 = Trader(exchange=exchange)

    trader_1.sell(30, 4)
    trader_1.sell(50, 5)
    trader_1.sell(5, 3)
    trader_2.buy(100, 1)
    print(exchange)

    trader_2.buy(40, 2)
    print(exchange)

    trader_1.buy(40, 5)
    print(exchange)
