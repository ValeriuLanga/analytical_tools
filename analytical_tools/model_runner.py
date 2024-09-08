import pandas as pd
import numpy as np

from data_sourcing import crypto_market_data, utils


class ModelRunner():

    def __init__(self, data: pd.DataFrame, models: dict): 
        self.__data = data
        self.__models = models

    def run_models(self):
        self.__data['returns'] = np.log(self.__data['close'] / self.__data['close'].shift(1))
        self.__data['direction'] = np.sign(self.__data['returns'])

        lag_cols = self.__create_lags(self.__data, 5)
        self.__data = self.__data.dropna()
        bin_cols = self.__create_bins(self.__data, lag_cols)
        self.__fit_models(self.__data, bin_cols, self.__models)
        self.__derive_positions(self.__data, bin_cols, self.__models)
        strat_returns_cols = self.__evaluate_strats(self.__data, self.__models)

        print(strat_returns_cols)
        print(self.__data[strat_returns_cols].sum().apply(np.exp))

    def __create_lags(self, data: pd.DataFrame, lags: int) -> list[str]:
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

    def __create_bins(self, data: pd.DataFrame, laggings_cols: list[str], bins=[0]) -> list[str]:
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


    def __fit_models(self, data: pd.DataFrame, bin_columns: list[str], models: dict) -> None:
        """Fits the models to the provided data
        
        All models suppliec in 'models' are used
        """
        for model_name in models.keys():
            models[model_name].fit(data[bin_columns], data['direction'])


    def __derive_positions(self, data: pd.DataFrame, bin_columns: list[str], models: dict) -> None:
        """Creates columns for the positions that each model takes

        """
        
        for model in models.keys():
            data['pos_' + model] = models[model].predict(data[bin_columns])


    def __evaluate_strats(self, data: pd.DataFrame, models: dict) -> list[str]:
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