import pandas as pd
import numpy as np
from config import RISK_FREE_RATE

def run_analysis(portfolio, log_file_path="trade_log.csv"):
    """
    Loads the trade log and computes a summary of performance metrics,
    using the final portfolio state for more accurate reporting.
    """
    try:
        trades_df = pd.read_csv(log_file_path)
    except FileNotFoundError:
        print("Analysis failed: trade_log.csv not found.")
        return

    starting_capital = portfolio.initial_capital
    ending_capital = portfolio.cash
    total_return_pct = ((ending_capital - starting_capital) / starting_capital) * 100 if starting_capital > 0 else 0

    if trades_df.empty:
        print("No trades were executed. Final portfolio value is unchanged.")
        # Print a simplified report if no trades occurred.
        print("\n--- STRATEGY PERFORMANCE ANALYSIS ---")
        print(f"{'Metric':<28} {'Value':>15}")
        print("-" * 44)
        print(f"{'Starting Capital:':<28} ${starting_capital:15.2f}")
        print(f"{'Ending Capital:':<28} ${ending_capital:15.2f}")
        print(f"{'Total Net P/L:':<28} ${ending_capital - starting_capital:15.2f}")
        print(f"{'Total Return:':<28} {total_return_pct:14.2f}%")
        print(f"{'Total Trades:':<28} {0:15d}")
        print("-" * 44)
        return

    # --- Basic Performance Metrics from Trade Log ---
    total_net_pl_from_log = trades_df['Net_PL'].sum()
    total_trades = len(trades_df)
    winning_trades = (trades_df['Net_PL'] > 0).sum()
    win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0

    gross_profit = trades_df[trades_df['Gross_PL'] > 0]['Gross_PL'].sum()
    gross_loss = abs(trades_df[trades_df['Gross_PL'] < 0]['Gross_PL'].sum())
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

    # --- Risk-Adjusted Performance Metrics ---
    trades_df = pd.to_datetime(trades_df, unit='s')
    daily_pl = trades_df.set_index('Execution_Timestamp').resample('D')['Net_PL'].sum()
    
    # MODIFIED: Use the accurate starting capital from the portfolio for return calculations.
    daily_returns = daily_pl / starting_capital

    # Sharpe Ratio Calculation
    avg_daily_return = daily_returns.mean()
    std_dev_returns = daily_returns.std()
    daily_rf_rate = RISK_FREE_RATE / 252

    sharpe_ratio = 0
    if std_dev_returns is not None and std_dev_returns > 0:
        sharpe_ratio = (avg_daily_return - daily_rf_rate) / std_dev_returns * np.sqrt(252)

    # Sortino Ratio Calculation
    negative_returns = daily_returns[daily_returns < 0]
    downside_deviation = negative_returns.std()

    sortino_ratio = 0
    if downside_deviation is not None and downside_deviation > 0:
        sortino_ratio = (avg_daily_return - daily_rf_rate) / downside_deviation * np.sqrt(252)

    # --- Print Summary Report ---
    print("\n--- STRATEGY PERFORMANCE ANALYSIS ---")
    print(f"{'Metric':<28} {'Value':>15}")
    print("-" * 44)
    # NEW: Added detailed portfolio-based metrics to the top of the report.
    print(f"{'Starting Capital:':<28} ${starting_capital:15.2f}")
    print(f"{'Ending Capital:':<28} ${ending_capital:15.2f}")
    print(f"{'Total Net P/L (Portfolio):':<28} ${ending_capital - starting_capital:15.2f}")
    print(f"{'Total Return:':<28} {total_return_pct:14.2f}%")
    print("-" * 44)
    print(f"{'Total Trades:':<28} {total_trades:15d}")
    print(f"{'Win Rate:':<28} {win_rate:14.2f}%")
    print(f"{'Profit Factor:':<28} {profit_factor:15.2f}")
    print(f"{'Annualized Sharpe Ratio:':<28} {sharpe_ratio:15.2f}")
    print(f"{'Annualized Sortino Ratio:':<28} {sortino_ratio:15.2f}")
    print("-" * 44)
