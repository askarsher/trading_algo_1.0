API_KEY = 'your_api_key_here'
API_SECRET = 'your_api_secret_here'
DB_CONN = 'your_db_connection_string_here'

#Assets
SYMBOLS = ['SPY']

#Portfolio capital in USD ($100k)
INITIAL_CAPITAL = 100000.0

# Data & Bar Aggregation Parameters
TICK_INTERVAL = 5  # seconds between ticks
BAR_INTERVAL_MINUTES = 1 # Aggregate 5-sec ticks into 1-min bars

# Mean Reversion Strategy Parameters
LOOKBACK_PERIOD = 20 # Number of bars for moving average
STD_DEV_MULTIPLIER = 2.0

# Market Simulation Parameters
EXECUTION_DELAY_MINUTES = 10
SLIPPAGE_PERCENT = 0.0005 # 0.05% slippage, more realistic than 1%
TRANSACTION_FEES = { # Sample fee structure 
    "ORF_PER_CONTRACT": 0.02685,
    "OCC_PER_CONTRACT": 0.02
}

# Option Pricing Parameters
RISK_FREE_RATE = 0.02 # Annualized ri rate
OPTION_EXPIRY_DAYS = 2 # Time to expiry for the barrier options
