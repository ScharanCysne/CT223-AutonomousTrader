import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import os

from Analysis import Analysis
from TinyRLAgent import Agent

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

# Load stock to trains TinyRL
stocks = ["BBAS3", "BBDC4", "ITUB4", "PETR4", "VALE3"]
# Read CSV into pandas dataframe and stores it in an numpy array
portfolio = np.array([pd.read_csv(os.path.join(THIS_FOLDER, f'input\\{stock}.csv'), sep="\t") for stock in stocks], dtype=object)
# Calculate the variations to each dataframe
rets = [stock['<CLOSE>'].diff()[1:] for stock in portfolio]
# Stores current price
prices = [stock['<CLOSE>'].values.tolist() for stock in portfolio]
# Identify each list of prices and variations
for i in range(len(stocks)):
    rets[i].name = stocks[i]

'''
csv_filename = os.path.join(THIS_FOLDER, 'input\\ITUB4.csv')
stock = pd.read_csv(csv_filename, sep="\t")
stock = stock.dropna()

rets = np.array(stock['<CLOSE>'].diff()[1:])
''' 

# Separating Train and Test Samples
N = int(0.7 * len(rets[0]))             # Number of Training Samples
P = len(rets[0]) - N                    # Number of Test Samples
x_train = [ret[:N] for ret in rets]     # Training Samples
x_test = [ret[-P:] for ret in rets]     # Test Samples
prices_train = [price[:N] for price in prices]
prices_test = [price[-P:] for price in prices]

# Normalization for stochastic optimization
stds = [np.std(training_data) for training_data in x_train]
means = [np.mean(training_data) for training_data in x_train]

for i in range(len(stocks)):
    x_train[i] = (x_train[i] - means[i]) / stds[i]    
    x_test[i] = (x_test[i] - means[i]) / stds[i]

# Hyper-parameters
epochs = 1000
learning_rate = 0.3
commission = 0.0025
capital = 10000

# Reinforcement Learning Agent
tinyRL = Agent(epochs, learning_rate, commission, capital, prices_train)
# Train Tiny RL in training samples
theta, sharpes = tinyRL.train(x_train)

# Save individual data
with open('fittest.txt', 'w') as f:
    print('Fittest Thetas Data.\n', file=f)
    print(f"Thetas optimized BBAS3: {theta[0]}", file=f)
    print(f"Sharpes associated: {sharpes[-1][0]}\n", file=f)
    print(f"Thetas optimized BBDC4: {theta[1]}", file=f)
    print(f"Sharpes associated: {sharpes[-1][1]}\n", file=f)
    print(f"Thetas optimized ITUB4: {theta[2]}", file=f)
    print(f"Sharpes associated: {sharpes[-1][2]}\n", file=f)
    print(f"Thetas optimized PETR4: {theta[3]}", file=f)
    print(f"Sharpes associated: {sharpes[-1][3]}\n", file=f)
    print(f"Thetas optimized VALE3: {theta[4]}", file=f)
    print(f"Sharpes associated: {sharpes[-1][4]}\n", file=f)

# Check results from training and testing
train_returns = tinyRL.returns(tinyRL.positions(x_train, theta), x_train, prices_train, 0.0025)
test_returns = tinyRL.returns(tinyRL.positions(x_test, theta), x_test, prices_test, 0.0025)

# Plot Sharpe Ration Convergence
plt.figure()
plt.plot(sharpes)
plt.xlabel('Epoch Number')
plt.ylabel('Sharpe Ratio')
plt.show()

# Plot Training Returns
plt.figure()
plt.xlabel('Ticks')
plt.ylabel('Cumulative Returns')
plt.legend(stocks)
plt.title("RL Model vs. Buy and Hold - Training Data")
for i in range(len(train_returns)):
    plt.plot(train_returns[i], label="Reinforcement Learning Model", linewidth=1)
    plt.plot(x_train[i], label="Buy and Hold", linewidth=1)
plt.show()

# Plot Test Returns
plt.figure()
plt.xlabel('Ticks')
plt.ylabel('Cumulative Returns')
plt.legend(stocks)
plt.title("RL Model vs. Buy and Hold - Test Data")
for i in range(len(test_returns)):
    plt.plot(test_returns[i], label="Reinforcement Learning Model", linewidth=1)
    plt.plot(x_test[i], label="Buy and Hold", linewidth=1)

plt.show()