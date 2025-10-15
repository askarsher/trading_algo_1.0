# API Trading Algorithm 
**Done by Vignesh and Askar for Prometheus Capital - UvA**

### Overview
This repository contains the code for a signal-based trading algorithm done by Quant Desk Analysts of Prometheus Capital - UvA, Vignesh and Askar. The algorithm itself is a result of a project assignment for Prometheus, the first of many. The algorithm would make use of an API to access real-time quotes of the underlying assets. A variety of assets can be chosen for this strategy, as it does not rely on sectoral dynamics. Instead, it makes use of simple yet effective momentum-based strategy: utilzing the mean-reversion and the Bollinger bands. 

### Structure
The following diagram visualizes the hierarchy according to which the algorithm operates. 
<img width="1207" height="511" alt="Untitled drawing (4)" src="https://github.com/user-attachments/assets/5e8cd755-dc05-4f3c-aed7-689c5a201430" />
To put it simply:
- Level 1: API access details and global defintions which will be used throughout the code
- Level 2: information retrieval, signal generation, pricing of options, and portfolio management
- Level 3: execution of orders based on signals and simulating market conditions
- Level 4: the main file responsible for running the backtest
- Level 5: calculation of performance ratios based on trade logs

### Rationale and Challenges
The Team resorted for using a mean-reversion strategy due to its proven succcess and quantitative edge. Although this strategy performs best in a HFT capacity - which is unavailable for us, as later mentioned - it still has many practical advantages, thus becoming our weapon of choice. The use of Bollinger bands is validated by the simplicity behind the implementation; it is a powerful tool for gauging market dynamics, which is convenient for coding and backtesting.

The team did not manage to secure API approval from known providers, thus the code uses a mock API and assumes the following abilities:
1. Information on asset prices, bid-ask spread
2. Granular data - one tick every 5 seconds
3. Presence of historical values at the same granularity, at least up to 15 trading days prior to the day of the backtest

The existence of options related data (e.g. price of the option contract, implied volatility surface) is not assumed and calculations are done to replicate them. The user **_must make sure_** to input the correct static information in the `config.py` such as `SYMBOLS`, `OPTION_EXPIRY_DAYS` among others according to their desired specification. Also, when running the backtest from `main.py`, the user will be asked to enter the date from which the backtest should start.

As the algorithm was written strictly in a retail trading capacity, it was important to replicate such conditions. One of the biggest challenges for retail traders is delayed market data (from 10-15 mins), which obviously has a huge impact on trading. We accounted for this delay be revalidating our signals through adding a _delay_ in our code. In the backtest, it would be as if the signal received at t=0 is first sent to a pending order. Once it's validated at t=1 (where 1 is the size of the _delay_), it will be moved from a pending order straight to execution. Granted, this setup is far from perfect, but it a step towards making the algorithm more realistic. 
