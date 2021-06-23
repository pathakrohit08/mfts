1. Market
    market.py will get real_time_data from scraper module and last n days data from load module.
    it will check for buy signal and sell signal

2. load
    load.py will calculate all the initial value for a asset and save it to the db. It will also be used
    to fetch data from db for last n days.

3. backtest
    any strategy can be used to backtest here

4. report
    generate report using matplotlib,co-relation matrix

5. connection
    this class is used to connect to the database
