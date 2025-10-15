import csv
from datetime import datetime

class Logger:
    """
    Handles the logging of all trade activities to a CSV file.
    """
    def __init__(self, log_file_path="trade_log.csv"):
        self.log_file_path = log_file_path
        self.open_trades = {}  # symbol -> trade_details
        self.trade_id_counter = 0
        self._initialize_log()

    def _initialize_log(self):
        """Creates the log file and writes the header row."""
        header = [
            "Trade_ID", "Symbol", "Direction", "Status", "Signal_Timestamp",
            "Entry_Execution_Timestamp", "Underlying_Price_at_Signal",
            "Underlying_Price_at_Entry", "Option_Type", "Strike_Price",
            "Barrier_Price", "Expiry_Days", "Entry_Price", "Entry_Fees",
            "Execution_Timestamp", "Underlying_Price_at_Exit", "Exit_Price",
            "Exit_Fees", "Gross_PL", "Net_PL"
        ]
        with open(self.log_file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)

    def log_trade_open(self, fill_details):
        """Records the details of an opened position in memory."""
        self.trade_id_counter += 1
        symbol = fill_details['order']['symbol']

        self.open_trades[symbol] = {
            "Trade_ID": self.trade_id_counter,
            "Symbol": symbol,
            "Direction": fill_details['order']['direction'],
            "Status": "OPEN",
            "Signal_Timestamp": fill_details['order']['submission_timestamp'],
            "Entry_Execution_Timestamp": fill_details['fill_timestamp'],
            "Underlying_Price_at_Signal": fill_details['order'].get('signal_price', 'N/A'),
            "Underlying_Price_at_Entry": fill_details['underlying_price_at_fill'],
            "Option_Type": fill_details['order']['type'],
            "Strike_Price": fill_details['order']['strike'],
            "Barrier_Price": fill_details['order'].get('barrier', 'N/A'),
            "Expiry_Days": fill_details['order'].get('expiry', 'N/A'),
            "Entry_Price": fill_details['fill_price'],
            "Entry_Fees": fill_details['fees']
        }
        print(f"Logged OPEN for Trade ID {self.trade_id_counter} on {symbol}")

    def log_trade_close(self, fill_details):
        """
        Closes an open trade, calculates P/L, and writes the complete
        record to the CSV log.
        """
        symbol = fill_details['order']['symbol']
        if symbol not in self.open_trades:
            print(f"Warning: Received close signal for {symbol} but no open trade found.")
            return

        trade = self.open_trades.pop(symbol)  # Retrieve and remove the open trade

        # Update trade with closing information
        trade["Status"] = "CLOSED"
        trade["Execution_Timestamp"] = fill_details['fill_timestamp']
        trade["Underlying_Price_at_Exit"] = fill_details['underlying_price_at_fill']
        trade["Exit_Price"] = fill_details['fill_price']
        trade["Exit_Fees"] = fill_details['fees']

        # Calculate Profit and Loss (assuming 1 contract for simplicity)
        trade["Gross_PL"] = trade["Exit_Price"] - trade["Entry_Price"]
        trade["Net_PL"] = trade["Gross_PL"] - (trade["Entry_Fees"] + trade["Exit_Fees"])

        # Write the completed trade record to the file
        with open(self.log_file_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(trade.values())

        print(f"Logged CLOSE for Trade ID {trade['Trade_ID']} on {symbol}. Net P/L: {trade['Net_PL']:.2f}")
