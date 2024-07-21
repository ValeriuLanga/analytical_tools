from data_sourcing import crypto_market_data as md

# symbols = ['SOL', 'BTC', 'ETH', 'AVAX']
symbols = ['SOL']
start_date = '2024-07-21'
end_date = '2023-07-21' # '2018-07-21 
time_unit = 'SIX_HOURS'

for sym in symbols:
    md.get_historical_ticks_as_df("{}-USD".format(sym), start_date, end_date, time_unit)