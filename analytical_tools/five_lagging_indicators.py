import pandas as pd
import numpy as np

import statsmodels.formula.api as sm
from pylab import mpl, plt

from sklearn import linear_model
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split

from data_sourcing import crypto_market_data, utils


def create_lags(data: pd.DataFrame, lags: int) -> list[str]:
    """Creates lagging returns columns

    Lagging returns will be added to the data frame.
     
    Returns
    -------
    list[str]
        a list with all the newly added lagging returns columns
    """

    cols = []

    for lag in range(1, lags + 1):
        col = "lag_{}".format(lag)
        data[col] = data['returns'].shift(lag)

        cols.append(col)
    
    return cols


def create_bins(data: pd.DataFrame, laggings_cols: list[str], bins=[0]) -> list[str]:
    """Puts the returns in bins

    Returns
    -------
    list[str]
        a list with all the newly added bins
    """

    cols_bin = []

    for col in laggings_cols:
        col_bin = col + '_bin'
        data[col_bin] = np.digitize(data[col], bins=bins)

        cols_bin.append(col_bin)

    return cols_bin


def fit_models(data: pd.DataFrame, bin_columns: list[str], models: dict) -> None:
    """Fits the models to the provided data
    
    All models suppliec in 'models' are used
    """
    for model_name in models.keys():
        models[model_name].fit(data[bin_columns], data['direction'])


def derive_positions(data: pd.DataFrame, bin_columns: list[str], models: dict) -> None:
    """Creates columns for the positions that each model takes

    """
    
    for model in models.keys():
        data['pos_' + model] = models[model].predict(data[bin_columns])


def evaluate_strats(data: pd.DataFrame, models: dict) -> list[str]:
    """Evaluates the returns that each of the models made
    
     Returns
    -------
    list[str]
        a list with all the column names that hold the models' performance
    """

    performance_cols = []

    for model in models.keys():
        col = 'strat_' + model
        data[col] = data['pos_' + model] * data['returns']

        performance_cols.append(col)

    performance_cols.insert(0, 'returns')

    return performance_cols


if __name__ == '__main__':
    # let's load SOL data

    sol_data = crypto_market_data.load_archived_market_data(
        'SOL-USD',
        start_date='2023-07-21',
        end_date='2024-07-21'
    )

    sol_data = sol_data.set_index('start')
    sol_data = sol_data.sort_index()

    sol_data['returns'] = np.log(sol_data['close'] / sol_data['close'].shift(1))
    sol_data['direction'] = np.sign(sol_data['returns'])

    lag_cols = create_lags(sol_data, 5)
    sol_data = sol_data.dropna()
    """
                            low    high    open   close         volume   returns  direction     lag_1     lag_2     lag_3     lag_4     lag_5
    start
    2023-07-22 06:00:00   25.41   25.89   25.68   25.61   57692.276000 -0.002730       -1.0  0.006250  0.000784  0.009061  0.000396 -0.004345
    2023-07-22 12:00:00   25.51   25.76   25.60   25.53   98644.850000 -0.003129       -1.0 -0.002730  0.006250  0.000784  0.009061  0.000396
    2023-07-22 18:00:00   24.06   25.53   25.53   24.54  340364.030000 -0.039550       -1.0 -0.003129 -0.002730  0.006250  0.000784  0.009061
    2023-07-23 00:00:00   24.16   24.91   24.53   24.84  374835.654000  0.012151        1.0 -0.039550 -0.003129 -0.002730  0.006250  0.000784
    2023-07-23 06:00:00   24.62   24.89   24.84   24.67  103303.922000 -0.006867       -1.0  0.012151 -0.039550 -0.003129 -0.002730  0.006250
    """
    
    bin_cols = create_bins(sol_data, lag_cols)
    """
                            low    high    open   close         volume   returns  direction     lag_1     lag_2     lag_3     lag_4     lag_5  lag_1_bin  lag_2_bin  lag_3_bin  lag_4_bin  lag_5_bin
    start
    2023-07-22 06:00:00   25.41   25.89   25.68   25.61   57692.276000 -0.002730       -1.0  0.006250  0.000784  0.009061  0.000396 -0.004345          1          1          1          1          0
    2023-07-22 12:00:00   25.51   25.76   25.60   25.53   98644.850000 -0.003129       -1.0 -0.002730  0.006250  0.000784  0.009061  0.000396          0          1          1          1          1
    2023-07-22 18:00:00   24.06   25.53   25.53   24.54  340364.030000 -0.039550       -1.0 -0.003129 -0.002730  0.006250  0.000784  0.009061          0          0          1          1          1
    2023-07-23 00:00:00   24.16   24.91   24.53   24.84  374835.654000  0.012151        1.0 -0.039550 -0.003129 -0.002730  0.006250  0.000784          0          0          0          1          1
    """

    C = 1 # Inverse of regularization strength
    models = {
        'log_reg': linear_model.LogisticRegression(C=C),
        'gauss_nb': GaussianNB(),
        'svm': SVC(C=C)
    }
    fit_models(sol_data, bin_cols, models)
    derive_positions(sol_data, bin_cols, models)
    strat_returns_cols = evaluate_strats(sol_data, models)

    # print(strat_returns_cols)
    # print(sol_data[strat_returns_cols].sum().apply(np.exp))
    """
    returns            6.744938     <- still good benchmark rets
    strat_log_reg      2.525373
    strat_gauss_nb     2.525373
    strat_svm         18.135043     <- overfitting + ~bull run
    """

    # sol_data[strat_returns_cols].cumsum().apply(np.exp).plot(figsize=(10, 6))
    # plt.show()

    ##############################################################################
    # now let's test this using a randomized train-test split
    train, test = train_test_split(sol_data, test_size=0.5, shuffle=True, random_state=100)
    train = train.copy().sort_index()
    test = test.copy().sort_index()

    fit_models(train, bin_cols, models)     # we do this on one random half of the data
    
    derive_positions(test, bin_cols, models)  # and the rest on the other half
    strat_returns_cols = evaluate_strats(test, models)

    print(test[strat_returns_cols].sum().apply(np.exp))
    """
    returns           2.222274
    strat_log_reg     1.122149
    strat_gauss_nb    1.122149
    strat_svm         1.755403      <- pretty grim; can't even beat benchmark
    """

    test[strat_returns_cols].cumsum().apply(np.exp).plot(figsize=(10, 6))
    plt.show()

